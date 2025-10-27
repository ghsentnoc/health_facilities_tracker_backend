from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail.errors import ConnectionErrors

from app.auth.config.auth_config import auth_config
from app.auth.custom_exceptions import AuthHTTPException
from app.auth.models import Role
from app.auth.schemas.mail_body import AccountVerificationTemplateBodySchema, ResetPasswordTemplateBodySchema
from app.auth.schemas.request.auth import (
    AccountVerificationResponseSchema,
    AlreadyVerifiedErrorDataSchema,
    AuthenticationTokenSchema,
    EmailSchema,
    PasswordResetSchema,
    TokenDataSchema,
)
from app.auth.services.token_service import TokenService
from app.auth.utils.constants import TokenTypeConstants
from app.auth.utils.hash_password import PasswordHashManager
from app.core.base_service import BaseService
from app.core.config.project_config import project_config
from app.core.custom_exceptions import ExpiredTokenError, FailedToSaveObjectException, InvalidTokenError
from app.core.mail_service import MailServiceBuilder
from app.core.utils.constants import ApplicationConstants
from app.core.utils.messages import ErrorMessages, SuccessMessages
from app.locations.models import Facility
from app.users.models import User, UserProfile
from app.users.repositories.user_repository import UserRepository
from app.users.schemas.request.user import CreateUserRequestSchema, CreateUserSchema
from app.users.schemas.request.user_profile import CreateUserProfileSchema


class AuthService(BaseService[User]):
    """The service class for 'user'."""

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        user_service: BaseService[User],
        user_profile_service: BaseService[UserProfile],
        facility_service: BaseService[Facility],
        role_service: BaseService[Role],
        password_hash_manager: PasswordHashManager,
        mail_service: MailServiceBuilder,
        token_service: TokenService,
    ) -> None:
        """Initializer for 'user' service.

        Args:
            user_repository (UserRepository): The user repository.
            user_service (BaseService[User]): The user service.
            user_profile_service (BaseService[UserProfile]): The user profile service.
            facility_service (BaseService[Facility]): The facility service.
            role_service (BaseService[Role]): The role service.
            password_hash_manager (PasswordHashManager): The manager for hashing and verifying passwords.
            mail_service (MailServiceBuilder): The mailing service.
            token_service (TokenService): The token service.
        """
        self.user_repository = user_repository
        self.user_service = user_service
        self.user_profile_service = user_profile_service
        self.facility_service = facility_service
        self.role_service = role_service
        self.password_hash_manager = password_hash_manager
        self.mail_service = mail_service
        self.token_service = token_service
        super().__init__(main_repository=user_repository)

    async def register_user(self, *, user_data: CreateUserRequestSchema) -> User:
        """Create a new user.

        Args:
            user_data (CreateUserSchema): The user data to create.

        Returns:
            User: The newly created user.
        """
        # check if roles exist.
        for role_id in user_data.role_ids:
            _ = self.role_service.get_by_id(entity_id=role_id)

        # check if facility exist.
        if user_data.user_profile.facility_id:
            _ = self.facility_service.get_by_id(entity_id=user_data.user_profile.facility_id)

        # user schema
        new_user_schema = CreateUserSchema(
            email=str(user_data.email),
            password_hash=self.password_hash_manager.hash_password(password=user_data.password),
            role_ids=user_data.role_ids,
        )

        # create user
        user = self._default_create(
            entity_schema=new_user_schema, unique_field_to_check="email", unique_field_value=str(new_user_schema.email)
        )

        # create user profile
        user_profile_schema = CreateUserProfileSchema(**user_data.user_profile.model_dump(), user_id=user.id)  # type: ignore
        user_profile = self.user_profile_service.create(user_profile_data=user_profile_schema)

        # create verification token
        verification_token = self.token_service.create_token(
            payload={"sub": user.id, "iss": ApplicationConstants.APP_NAME.value},
            expires_in_minutes=auth_config.VERIFICATION_LINK_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.ACCOUNT_VERIFICATION_TOKEN.value,
        )

        # create verification link
        verification_link = f"{project_config.FRONTEND_URL}/auth/verify-account?token={verification_token}"

        # create account verification template body schema
        body = AccountVerificationTemplateBodySchema(
            app_name=ApplicationConstants.APP_NAME.value,
            first_name=str(user_profile.first_name),
            title="User Account Verification",
            code_expires_in_hours=24,
            current_year=datetime.now(tz=timezone.utc).year,
            verification_url=verification_link,
        ).model_dump()

        # build mail service
        (
            self.mail_service.subject(subject="Account Creation")
            .recipients(recipients=[user.email])  # type: ignore
            .template(template_name="account_creation.html")
            .body(body=body)
        )

        # send the mail
        try:
            await self.mail_service.send_mail()
        except ConnectionErrors:
            await self.mail_service.send_mail()

        return user

    def verify_account(self, *, token_data: TokenDataSchema) -> AccountVerificationResponseSchema:
        """Verify a user's account by verifying their token.

        Args:
            token_data (TokenDataSchema): The token data to verify.

        Returns:
            AccountVerificationResponseSchema: The response after verification is successful.
        """
        # decode the token
        # raise error if token is invalid or expired
        try:
            decoded_token = self.token_service.decode_token(token=token_data.token)
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e
        except ExpiredTokenError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

        # check if the token is an account verification token
        if decoded_token.get("token_type") != TokenTypeConstants.ACCOUNT_VERIFICATION_TOKEN.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INVALID_TOKEN.value)

        # check if the user exists
        if not self.user_service.check_if_exists_and_not_deleted(
            field_name="id", value=decoded_token["sub"], operator="eq"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=User, value=decoded_token["sub"]),
            )

        # get the user to verify
        user_to_verify = self.user_service.get_by_id(entity_id=decoded_token["sub"])

        # raise an error if the is user is already verified
        if user_to_verify.is_verified:
            raise AuthHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                data=AlreadyVerifiedErrorDataSchema(
                    email=user_to_verify.email,  # type: ignore
                    is_verified=bool(user_to_verify.is_verified),
                ).model_dump(),
                message=ErrorMessages.ALREADY_VERIFIED.value,
            )

        # set is verified to true on user
        user_to_verify.is_verified = True  # type: ignore

        # verify and save user.
        try:
            verified_user = self.user_repository.save(object_to_save=user_to_verify)
        except FailedToSaveObjectException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

        # create response after verifying user
        response = AccountVerificationResponseSchema(
            email=verified_user.email,  # type: ignore
            message=SuccessMessages.VERIFIED.value,
            is_verified=bool(verified_user.is_verified),
        )

        return response

    async def resend_account_verification_email(self, *, resend_account_verification_email_data: EmailSchema) -> str:
        """Resend the account verification email

        Args:
            resend_account_verification_email_data (EmailStr): The resend account verification email data

        Returns:
            str: The response message
        """
        # check if the user exists
        if not self.user_service.check_if_exists_and_not_deleted(
            field_name="email", value=str(resend_account_verification_email_data.email).strip().lower(), operator="eq"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(
                    entity_type=User, value=str(resend_account_verification_email_data.email).strip().lower()
                ),
            )

        # get the user
        user = self.user_service.get_by_field(
            field_name="email", value=str(resend_account_verification_email_data.email).strip().lower(), operator="eq"
        )

        # raise error if user is already verified
        if user.is_verified:  # type: ignore
            raise AuthHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                data=AlreadyVerifiedErrorDataSchema(email=user.email, is_verified=user.is_verified).model_dump(),  # type: ignore
                message=ErrorMessages.ALREADY_VERIFIED.value,
            )

        # create verification token
        verification_token = self.token_service.create_token(
            payload={"sub": user.id, "iss": ApplicationConstants.APP_NAME.value},  # type: ignore
            expires_in_minutes=auth_config.VERIFICATION_LINK_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.ACCOUNT_VERIFICATION_TOKEN.value,
        )

        # create verification link
        verification_link = f"{project_config.FRONTEND_URL}/auth/verify-account?token={verification_token}"

        # create verification mail template body
        body = AccountVerificationTemplateBodySchema(
            app_name=ApplicationConstants.APP_NAME.value,
            first_name=user.to_dict().get("first_name"),  # type: ignore
            title="User Account Verification",
            code_expires_in_hours=24,
            current_year=datetime.now(tz=timezone.utc).year,
            verification_url=verification_link,
        ).model_dump()

        # build mail service
        (
            self.mail_service.subject(subject="User Account Verification")
            .template(template_name="account_creation.html")
            .body(body=body)
            .recipients(recipients=[user.email])  # type: ignore
        )

        # send verification mail
        try:
            await self.mail_service.send_mail()
        except ConnectionErrors:
            await self.mail_service.send_mail()

        return SuccessMessages.VERIFICATION_EMAIL_SENT.value

    async def request_password_reset(self, *, email_data: EmailSchema) -> str:
        """Request for password reset

        Args:
            email_data (EmailSchema): The user email data

        Returns:
            str: The password reset request response
        """
        # check if the user exists
        if not self.user_service.check_if_exists_and_not_deleted(
            field_name="email", value=str(email_data.email).strip().lower(), operator="eq"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(
                    entity_type=User, value=str(email_data.email).strip().lower()
                ),
            )

        # get the user
        user = self.user_service.get_by_field(
            field_name="email", value=str(email_data.email).strip().lower(), operator="eq"
        )

        # Check if the user is verified
        if not user.is_verified:  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.NOT_VERIFIED.value)

        # Generate a reset verification token
        password_reset_verification_token = self.token_service.create_token(
            payload={"sub": user.id, "iss": ApplicationConstants.APP_NAME.value},  # type: ignore
            expires_in_minutes=auth_config.RESET_PASSWORD_TOKEN_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.PASSWORD_RESET_TOKEN.value,
        )

        # create verification link
        verification_link = (
            f"{project_config.FRONTEND_URL}/auth/reset-password?token={password_reset_verification_token}"
        )

        # Send the reset code to the user's email
        mail_body = ResetPasswordTemplateBodySchema(
            title="Password Reset Request",
            first_name=user.to_dict().get("first_name"),  # type: ignore
            code_expires_in_minutes=auth_config.RESET_PASSWORD_TOKEN_EXPIRES_IN_MINUTES,
            app_name=ApplicationConstants.APP_NAME.value,
            current_year=datetime.now(tz=timezone.utc).year,
            verification_url=verification_link,
        )

        # Send the email
        (
            self.mail_service.subject(subject="Password Reset Request")
            .template(template_name="reset_password.html")
            .body(body=mail_body.model_dump())
            .recipients(recipients=[user.email])  # type: ignore
        )

        try:
            await self.mail_service.send_mail()
        except ConnectionErrors:
            await self.mail_service.send_mail()

        return SuccessMessages.RESET_PASSWORD_EMAIL_SENT.value

    def verify_password_reset_token(self, *, token_data: TokenDataSchema) -> dict:
        """Verify the password reset token

        Args:
            token_data (TokenDataSchema): The password reset token data

        Returns:
            str: The verification response
        """
        # decode the token
        # raise error if token is invalid or expired
        try:
            decoded_token = self.token_service.decode_token(token=token_data.token)
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e
        except ExpiredTokenError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

        if decoded_token.get("token_type") != TokenTypeConstants.PASSWORD_RESET_TOKEN.value:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INVALID_TOKEN.value)

        # get the user to verify
        user = self.user_service.get_by_id(entity_id=decoded_token["sub"])  # type: ignore

        return {"email": user.email, "id": user.id}  # type: ignore

    def reset_password(self, *, password_reset_data: PasswordResetSchema) -> str:
        """Reset the user's password

        Args:
            password_reset_data (ResetPassword): The password reset data

        Returns:
            str: The password reset response
        """
        # verify password reset token
        verification_response = self.verify_password_reset_token(
            token_data=TokenDataSchema(token=password_reset_data.token)
        )

        # get the user to verify
        user = self.user_service.get_by_id(entity_id=verification_response.get("id"))  # type: ignore

        if user.email != str(password_reset_data.email).strip().lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INVALID_EMAIL.value)

        # set user password to new password
        user.password = self.password_hash_manager.hash_password(password=password_reset_data.password)

        # invalidate all token versions
        user.token_version += 1  # type: ignore

        try:
            self.user_repository.save(object_to_save=user)
        except FailedToSaveObjectException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

        return SuccessMessages.PASSWORD_RESET.value

    def authenticate_user(self, *, user_credentials: OAuth2PasswordRequestForm) -> AuthenticationTokenSchema:
        """Authenticate a user.

        Args:
            user_credentials (OAuth2PasswordRequestForm): The user credentials needed to perform authentication

        Returns:
            AuthenticationTokenSchema: The tokens after authenticating user.
        """
        # check if the user exists
        if not self.user_service.check_if_exists_and_not_deleted(
            field_name="email", value=str(user_credentials.username).strip().lower(), operator="eq"
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(
                    entity_type=User, value=str(user_credentials.username).strip().lower()
                ),
            )

        # get the user
        user = self.user_service.get_by_field(
            field_name="email", value=str(user_credentials.username).strip().lower(), operator="eq"
        )

        if not user.is_verified:  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.NOT_VERIFIED.value)

        if not user.is_approved:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.entity_not_approved(object_type=User, value=user.email),  # type: ignore
            )

        if not self.password_hash_manager.verify_password(
            plain_password=user_credentials.password,
            hashed_password=user.password_hash,  # type: ignore
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INVALID_CREDENTIALS.value)

        payload = {"sub": user.id, "iss": ApplicationConstants.APP_NAME.value, "token_version": user.token_version}  # type: ignore

        access_token = self.token_service.create_token(
            payload=payload,
            expires_in_minutes=auth_config.ACCESS_TOKEN_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.ACCESS_TOKEN.value,
        )
        refresh_token = self.token_service.create_token(
            payload=payload,
            expires_in_minutes=auth_config.REFRESH_TOKEN_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.REFRESH_TOKEN.value,
        )

        user.is_logged = True  # type: ignore
        user.last_login = datetime.now(tz=timezone.utc)  # type: ignore

        try:
            self.user_repository.save(object_to_save=user)  # type: ignore
        except FailedToSaveObjectException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

        return AuthenticationTokenSchema(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

    # def change_user_role(self, *, user_id: str, role_data: UpdateUserRoleSchema) -> User:
    #     """Change a user's role."""

    def create(self, *args, **kwargs) -> User:  # type: ignore
        """Create a user"""
        raise NotImplementedError

    def update(self, *args, **kwargs) -> User:  # type: ignore
        """Update a user."""
        raise NotImplementedError

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[User]:
        """Get all entities"""
        raise NotImplementedError

    def delete(self, *, entity_id: str) -> User:
        """Delete an entity."""
        raise NotImplementedError

    def get_by_id(self, *, entity_id: str) -> User:
        """Get an entity by id."""
        raise NotImplementedError

    def get_total_pages(self, pagination: Optional[str]) -> int:
        """Get total pages."""
        raise NotImplementedError

    def get_pagination_extras(self, request: Request) -> dict:
        """Get pagination extras"""
        raise NotImplementedError

    def get_total_number(self) -> int:
        """Get total number"""
        raise NotImplementedError

    def restore(self, *, entity_id: str) -> User:
        """Restore entity"""
        raise NotImplementedError
