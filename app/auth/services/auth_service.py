import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from fastapi import HTTPException, Request, status

from app.auth.config.auth_config import auth_config
from app.auth.custom_exceptions import AuthHTTPException
from app.auth.models import Application, AuthSession, Role
from app.auth.schemas.mail_body import AccountVerificationTemplateBodySchema, ResetPasswordTemplateBodySchema
from app.auth.schemas.request.auth import (
    AccountSuspendedResponseSchema,
    AccountVerificationResponseSchema,
    AlreadyVerifiedOrPasswordSetDataSchema,
    AuthenticationForm,
    AuthenticationTokenSchema,
    ChangePasswordSchema,
    EmailSchema,
    LoggedOutResponseSchema,
    PasswordResetSchema,
    SwitchRoleSchema,
    TokenDataSchema,
    TokensRevokedResponseSchema,
    UpdateUserRoleSchema,
)
from app.auth.schemas.request.auth_session import CreateAuthSessionSchema
from app.auth.schemas.request.refresh_token import CreateRefreshTokenSchema
from app.auth.services.auth_session_service import AuthSessionService
from app.auth.services.token_service import TokenService
from app.auth.utils.constants import (
    INTERNAL_APPLICATION_ALLOWED_ROLES,
    RefreshTokenRevocationReasons,
    TokenTypeConstants,
)
from app.auth.utils.hash_password import PasswordHashManager
from app.core.config.project_config import project_config
from app.core.custom_exceptions import (
    ExpiredTokenError,
    FailedToSaveObjectException,
    InvalidTokenError,
)
from app.core.schemas.notification_schemas import EmailNotificationMessageSchema
from app.core.services.base_service import BaseService
from app.core.services.notification_publisher_service import NotificationPublisherService
from app.core.utils.constants import ApplicationConstants
from app.core.utils.messages import ErrorMessages, SuccessMessages
from app.users.models import User
from app.users.repositories.user_repository import UserRepository


class AuthService(BaseService[User]):
    """The service class for 'user'.

    This class contains authentication related business logic for users.
    Private helper methods are provided to remove duplication when working
    with users, tokens, refresh token persistence and sending mail.
    """

    def _get_or_update_auth_session(
        self, *, user_id: str, device_id: str, client_type: Literal["web", "mobile", "api", "desktop", "cli"]
    ) -> AuthSession:
        """Get or create/update an auth session for a user and device."""
        try:
            auth_session = self.auth_session_service.get_session_by_device_id_user_id(
                device_id=device_id,
                user_id=user_id,
                client_type=client_type,
            )
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                auth_session = self.auth_session_service.create(
                    auth_session_data=CreateAuthSessionSchema(
                        user_id=user_id,
                        device_id=device_id,
                        client_type=client_type,
                        token_version=1,
                    )
                )
            else:
                raise e
        else:
            auth_session.token_version += 1  # type: ignore
            self.auth_session_service.main_repository.save(object_to_save=auth_session)  # type: ignore
        return auth_session  # type: ignore

    def _issue_tokens_and_refresh(
        self, *, user: User, active_role: str | None, auth_session: AuthSession, reason: str
    ) -> AuthenticationTokenSchema:
        """Issue tokens and persist refresh token for a user and session."""
        access_token, refresh_token, refresh_token_id = self._issue_tokens_for_user(
            user=user,
            active_role=active_role,
            auth_session=auth_session,
        )
        self._persist_user_and_create_refresh(
            user=user,
            plain_refresh_token=refresh_token,
            token_id=refresh_token_id,
            reason=reason,
        )
        return AuthenticationTokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            extra_info={"first_time_login": getattr(user, "first_time_login", False)},
        )

    def _get_user_for_authentication(self, *, user_credentials: AuthenticationForm) -> User:
        """Look up a user by the supplied authentication identifier."""
        identifier_value = str(user_credentials.username).strip()
        if user_credentials.user_identifier == "email":
            identifier_value = identifier_value.lower()

        user = self.user_repository.get_by_auth_identifier(
            identifier_type=user_credentials.user_identifier,
            value=identifier_value,
        )

        if user is None or user.is_deleted:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_CREDENTIALS.value,
            )

        return user

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        user_service: BaseService[User],
        role_service: BaseService[Role],
        refresh_token_service: Any,
        password_hash_manager: PasswordHashManager,
        token_service: TokenService,
        auth_session_service: AuthSessionService,
        notification_publisher: NotificationPublisherService,
    ) -> None:
        """Initializer for 'user' service.

        Args:
            user_repository (UserRepository): The user repository.
            oauth_account_repository (OAuthAccountRepository): The oauth account repository.
            user_service (BaseService[User]): The user service.
            user_profile_service (UserProfileService): The user profile service.
            role_service (BaseService[Role]): The role service.
            refresh_token_service (BaseService[RefreshToken]): The refresh token service.
            password_hash_manager (PasswordHashManager): The manager for hashing and verifying passwords.
            token_service (TokenService): The token service.
            google_oauth_service (GoogleOAuthService): The Google OAuth service.
            auth_session_service (AuthSessionService): The auth session service.
            notification_publisher (NotificationPublisherService): The notification publisher service.
        """
        self.user_repository = user_repository
        self.user_service = user_service
        self.role_service = role_service
        self.refresh_token_service = refresh_token_service
        self.password_hash_manager = password_hash_manager
        self.token_service = token_service
        self.auth_session_service = auth_session_service
        self.notification_publisher = notification_publisher
        super().__init__(main_repository=user_repository)

    # --------------------------- Helper methods (DRY) ---------------------------
    def _user_valid_for_login(self, *, user: User) -> None:
        """Check if the user is valid for login.

        Args:
            user (User): The user to check.
        """
        if not user.is_verified:  # type: ignore
            raise AuthHTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                data=self._already_verified_schema(user=user),  # type: ignore
                message=ErrorMessages.NOT_VERIFIED.value,
            )

        # check if user is approved
        if not user.is_approved:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.entity_not_approved(object_type=User, value=str(user.email)),
            )

        # check if user is suspended
        if user.is_suspended:  # type: ignore
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorMessages.ACCOUNT_SUSPENDED.value)

    def _get_user_by_field_or_404(self, *, field_name: str, value: Any) -> User | list[User]:
        """Ensure a user exists (and not deleted) and return it.

        Args:
            field_name: Name of the field to query by.
            value: Value to query.

        Returns:
            User: The found user.

        Raises:
            HTTPException: If the user does not exist.
        """
        if not self.user_service.check_if_exists_and_not_deleted(field_name=field_name, value=value, operator="eq"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=User, value=value),
            )

        return self.user_service.get_by_field(field_name=field_name, value=value, operator="eq")

    def _save_user(self, *, user: User) -> User:
        """Save a user and translate repository save errors to HTTP 500.

        Args:
            user: The user object to save.

        Returns:
            User: The saved user.

        Raises:
            HTTPException: On persistence error.
        """
        try:
            return self.user_repository.save(object_to_save=user)
        except FailedToSaveObjectException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    def _persist_user_and_revoke(self, *, user: User, reason: str) -> User:
        """Save the user and revoke their refresh tokens.

        Args:
            user: The user to save.
            reason: The reason to pass to revoke_refresh_tokens.

        Returns:
            User: The saved user.
        """
        saved_user = self._save_user(user=user)
        self.refresh_token_service.revoke_refresh_tokens(user_id=saved_user.id, reason=reason)
        return saved_user

    def _persist_user_and_create_refresh(
        self, *, user: User, plain_refresh_token: str, token_id: str, reason: str
    ) -> User:
        """Persist user, revoke old tokens and create a new refresh token record.

        Args:
            user: The user to persist.
            plain_refresh_token: The plain refresh token to hash and store.
            token_id: The token id (uuid) used in the token payload.
            reason: Revocation reason for old tokens.

        Returns:
            User: The saved user.
        """
        hashed_refresh_token = self.password_hash_manager.hash_password(password=plain_refresh_token)
        saved_user = self._save_user(user=user)
        # revoke previous tokens and create the new one
        self.refresh_token_service.revoke_refresh_tokens(
            user_id=saved_user.id, new_token=hashed_refresh_token, reason=reason
        )
        self.refresh_token_service.create(
            refresh_token_data=CreateRefreshTokenSchema(
                user_id=str(saved_user.id),
                token_id=str(token_id),
                token=hashed_refresh_token,
                expires_at=datetime.now(tz=timezone.utc)
                + timedelta(minutes=auth_config.REFRESH_TOKEN_EXPIRES_IN_MINUTES),
                revoked=False,
            )
        )
        return saved_user

    def _issue_tokens_for_user(
        self, *, user: User, auth_session: AuthSession, active_role: Optional[str] = None
    ) -> tuple[str, str, str]:
        """Create access and refresh tokens for a user.

        Args:
            user: The user to create tokens for.
            auth_session (AuthSession): The auth session.
            active_role: Optional active role to embed in the access token.

        Returns:
            Tuple of (access_token, refresh_token, refresh_token_id)
        """
        payload = {
            "sub": user.id,
            "iss": ApplicationConstants.APP_NAME.value,
            "token_version": user.token_version,
            "session_id": str(auth_session.id),
            "session_token_version": str(auth_session.token_version),
            "active_role": active_role,
            "user_roles": [role.name for role in user.roles],
        }
        refresh_token_payload = {
            "sub": user.id,
            "session_id": str(auth_session.id),
            "iss": ApplicationConstants.APP_NAME.value,
            "token_id": str(uuid.uuid4()),
        }

        access_token = self.token_service.create_token(
            payload=payload,
            expires_in_minutes=auth_config.ACCESS_TOKEN_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.ACCESS_TOKEN.value,
        )
        refresh_token = self.token_service.create_token(
            payload=refresh_token_payload,
            expires_in_minutes=auth_config.REFRESH_TOKEN_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.REFRESH_TOKEN.value,
        )

        return access_token, refresh_token, refresh_token_payload.get("token_id")  # type: ignore

    @staticmethod
    def _already_verified_schema(*, user: User) -> dict:
        """Return the AlreadyVerifiedOrPasswordSetDataSchema for the given user."""
        return AlreadyVerifiedOrPasswordSetDataSchema(
            email=user.email,  # type: ignore
            is_verified=bool(user.is_verified),
        ).model_dump()

    # --------------------------- End helpers ---------------------------

    def verify_account(self, *, token_data: TokenDataSchema) -> AccountVerificationResponseSchema:
        """Verify a user's account by verifying their token.

        Args:
            token_data (TokenDataSchema): The token data to verify.

        Returns:
            AccountVerificationResponseSchema: The response after verification is successful.
        """
        # decode the token
        # raise error if the token is invalid or expired
        try:
            decoded_token = self.token_service.decode_token(token=token_data.token)
        except InvalidTokenError as e:
            raise AuthHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, message=str(e), data={"invalid": True}
            ) from e
        except ExpiredTokenError as e:
            raise AuthHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, message=str(e), data={"expired": True}
            ) from e

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

        # raise an error if the user is already verified
        if user_to_verify.is_verified:
            raise AuthHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                data=AlreadyVerifiedOrPasswordSetDataSchema(
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
            is_verified=bool(verified_user.is_verified),  # type: ignore
            roles=[role.to_dict() for role in verified_user.roles],  # type: ignore
        )

        return response

    async def resend_account_verification_email(
        self, *, resend_account_verification_email_data: EmailSchema, application: Application
    ) -> str:
        """Resend the account verification email

        Args:
            resend_account_verification_email_data (EmailStr): The resend account verification email data
            application (Application): The application making the request.

        Returns:
            str: The response message
        """
        # get the user and ensure exists
        user = self._get_user_by_field_or_404(
            field_name="email", value=str(resend_account_verification_email_data.email).strip().lower()
        )

        # raise error if user is already verified
        if user.is_verified:  # type: ignore
            raise AuthHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                data=self._already_verified_schema(user=user),  # type: ignore
                message=ErrorMessages.ALREADY_VERIFIED.value,
            )

        # set app name and app platform from header
        app_name = str(application.app_name)
        app_platform = str(application.platform)

        # use existing helper to send verification email (it will create a fresh token)
        await self._send_verification_email(
            user=user,  # type: ignore
            user_profile=user.profile,  # type: ignore
            app_name=app_name,
            app_platform=app_platform,  # type: ignore
        )

        return SuccessMessages.VERIFICATION_EMAIL_SENT.value

    async def request_password_reset(self, *, application: Application, email_data: EmailSchema) -> str:
        """Request for password reset

        Args:
            application (Application): The application making the request.
            email_data (EmailSchema): The user email data

        Returns:
            str: The password reset request response
        """
        # get the user
        user = self._get_user_by_field_or_404(field_name="email", value=str(email_data.email).strip().lower())

        # Check if the user is verified
        if not user.is_verified:  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.NOT_VERIFIED.value)

        # Generate a reset verification token
        password_reset_verification_token = self.token_service.create_token(
            payload={"sub": user.id, "iss": ApplicationConstants.APP_NAME.value},  # type: ignore
            expires_in_minutes=auth_config.RESET_PASSWORD_TOKEN_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.PASSWORD_RESET_TOKEN.value,
        )

        # set app name and app platform from header
        app_name = str(application.app_name)
        app_platform = str(application.platform)

        # create verification link
        verification_link = (
            f"{project_config.FRONTEND_URL}/auth/reset-password?token={password_reset_verification_token}"
        )

        # if app_platform attach to verification link
        if app_platform:
            verification_link = verification_link + f"&app_platform={app_platform}"

        # if app_name attach to verification link
        if app_name:
            verification_link = verification_link + f"&app_name={app_name}"

        # Send the reset code to the user's email
        mail_body = ResetPasswordTemplateBodySchema(
            title="Password Reset Request",
            first_name=user.to_dict().get("first_name"),  # type: ignore
            code_expires_in_minutes=auth_config.RESET_PASSWORD_TOKEN_EXPIRES_IN_MINUTES,
            app_name=ApplicationConstants.APP_NAME.value,
            current_year=datetime.now(tz=timezone.utc).year,
            verification_url=verification_link,
        )

        message = EmailNotificationMessageSchema(
            notification_type="password_reset",
            subject="Password Reset Request",
            recipients=[str(user.email)],  # type: ignore
            template_name="reset_password.html",
            body=mail_body.model_dump(),
        )
        await asyncio.to_thread(self.notification_publisher.publish_email_notification, message=message)

        return SuccessMessages.RESET_PASSWORD_EMAIL_SENT.value

    def verify_password_reset_token(self, *, token_data: TokenDataSchema) -> dict:
        """Verify the password reset token

        Args:
            token_data (TokenDataSchema): The password reset token data

        Returns:
            str: The verification response
        """
        # decode the token
        # raise error if the token is invalid or expired
        try:
            decoded_token = self.token_service.decode_token(token=token_data.token)
        except (InvalidTokenError, ExpiredTokenError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ) from e

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
        user.password_hash = self.password_hash_manager.hash_password(
            password=password_reset_data.password  # type: ignore
        )
        # invalidate all token versions
        user.token_version += 1  # type: ignore

        # save and revoke
        _ = self._persist_user_and_revoke(user=user, reason=RefreshTokenRevocationReasons.USER_PASSWORD_CHANGED.value)

        # revoke all auth sessions for user
        self.auth_session_service.revoke_auth_sessions_by_user_id(user_id=str(user.id))  # type: ignore

        return SuccessMessages.PASSWORD_RESET.value

    def authenticate_user(
        self,
        *,
        user_credentials: AuthenticationForm,
        application: Application,
        device_id: str,
        client_type: Literal["web", "mobile", "api", "desktop", "cli"],
    ) -> AuthenticationTokenSchema:
        """Authenticate a user.

        Args:
            user_credentials (OAuth2PasswordRequestForm): The user credentials needed to perform authentication
            application (Application): The application making the request.
            device_id (str): The device ID of the user.
            client_type (str): The client type of the user.

        Returns:
            AuthenticationTokenSchema: The tokens after authenticating user.
        """
        user = self._get_user_for_authentication(user_credentials=user_credentials)

        # check if user is valid for login
        self._user_valid_for_login(user=user)  # type: ignore

        # verify password
        if not self.password_hash_manager.verify_password(
            plain_password=user_credentials.password,
            hashed_password=user.password_hash,  # type: ignore
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorMessages.INVALID_CREDENTIALS.value
            )

        # get user active role
        user_active_role = self._get_current_user_active_role(user=user, application=application)  # type: ignore

        auth_session = self._get_or_update_auth_session(
            user_id=str(user.id),  # type: ignore
            device_id=device_id,
            client_type=client_type,
        )

        if user.last_login is not None:  # type: ignore
            user.first_time_login = False  # type: ignore

        # update user is_logged and token_version
        user.is_logged = True  # type: ignore
        user.last_login = datetime.now(tz=timezone.utc)  # type: ignore

        return self._issue_tokens_and_refresh(
            user=user,  # type: ignore
            active_role=user_active_role,
            auth_session=auth_session,
            reason=RefreshTokenRevocationReasons.USER_REAUTHENTICATED.value,
        )

    def refresh_token(
        self, *, token: TokenDataSchema, device_id: str, client_type: Literal["web", "mobile", "api", "desktop", "cli"]
    ) -> AuthenticationTokenSchema:
        """Refresh the user's token

        Args:
            token (TokenDataSchema): The refresh token
            device_id (str): The device ID of the user.
            client_type (str): The client type of the user.

        Returns:
            AuthenticationTokenSchema: The new token
        """
        # decode token
        try:
            payload = self.token_service.decode_token(token=token.token)
        except (ExpiredTokenError, InvalidTokenError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

        # throw error if token is not refresh token
        if payload.get("token_type") != TokenTypeConstants.REFRESH_TOKEN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = self.user_service.get_by_id(entity_id=payload["sub"])

        auth_session = self.auth_session_service.get_by_id(entity_id=payload["session_id"])
        if (
            str(auth_session.user_id) != str(user.id)
            or str(auth_session.device_id) != device_id
            or str(auth_session.client_type) != client_type
            or bool(auth_session.is_deleted)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ErrorMessages.INVALID_TOKEN.value,
                headers={"WWW-Authenticate": "Bearer"},
            )

        # retrieve token from refresh tokens
        refresh_token_obj = self.refresh_token_service.get_by_field(
            field_name="token_id", value=payload.get("token_id"), operator="eq"
        )

        # check if the token has been revoked
        if refresh_token_obj.revoked:  # type: ignore
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INVALID_TOKEN.value)

        auth_session = self._get_or_update_auth_session(
            user_id=str(user.id),
            device_id=device_id,
            client_type=client_type,
        )

        return self._issue_tokens_and_refresh(
            user=user,
            active_role=None,
            auth_session=auth_session,
            reason=RefreshTokenRevocationReasons.TOKEN_ROTATION.value,
        )

    def logout(
        self, *, current_user: User, device_id: str, client_type: Literal["web", "mobile", "api", "desktop", "cli"]
    ) -> LoggedOutResponseSchema:
        """Log a user out of the system

        Args:
            current_user (User): The current user logged in
            device_id (str): The device ID of the user.
            client_type (str): The client type of the user.

        Returns:
            dict: The logout response
        """
        current_user.is_logout = True  # type: ignore
        # current_user.token_version += 1  # type: ignore

        # get auth session
        auth_session = self.auth_session_service.get_session_by_device_id_user_id(
            device_id=device_id,
            user_id=str(current_user.id),
            client_type=client_type,
        )

        # invalidate auth session
        auth_session.token_version += 1  # type: ignore

        # save auth session
        self.auth_session_service.main_repository.save(object_to_save=auth_session)  # type: ignore

        # save user and revoke tokens
        self._persist_user_and_revoke(user=current_user, reason=RefreshTokenRevocationReasons.USER_LOGOUT.value)

        return LoggedOutResponseSchema(is_logout=bool(current_user.is_logout))

    def logout_all_sessions(self, *, current_user: User) -> LoggedOutResponseSchema:
        """Log the user out of all sessions.

        Args:
            current_user (User): The current user logged in.

        Returns:
            dict: The logout response.
        """
        current_user.is_logout = True  # type: ignore
        current_user.token_version += 1  # type: ignore

        # save user and revoke tokens
        self._persist_user_and_revoke(
            user=current_user, reason=RefreshTokenRevocationReasons.USER_LOGOUT_ALL_SESSIONS.value
        )

        # revoke all auth sessions for user
        self.auth_session_service.revoke_auth_sessions_by_user_id(user_id=str(current_user.id))  # type: ignore

        return LoggedOutResponseSchema(is_logout=bool(current_user.is_logout))

    def change_password(self, *, current_active_user: User, change_password_data: ChangePasswordSchema) -> User:
        """Change the password of a user.

        Args:
            current_active_user (User): The current logged-in user.
            change_password_data (ChangePasswordSchema): The change password data.

        Returns:
            User: The updated user object.
        """
        # check if user is verified
        if not current_active_user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.NOT_VERIFIED.value)

        # verify user's current password
        if not self.password_hash_manager.verify_password(
            plain_password=change_password_data.current_password, hashed_password=str(current_active_user.password_hash)
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INVALID_PASSWORD.value)

        # hash new password
        current_active_user.password_hash = self.password_hash_manager.hash_password(  # type: ignore
            password=change_password_data.new_password
        )
        current_active_user.token_version += 1  # type: ignore

        # save new password and revoke all tokens
        updated_user = self._persist_user_and_revoke(
            user=current_active_user, reason=RefreshTokenRevocationReasons.USER_PASSWORD_CHANGED.value
        )

        # revoke all auth sessions for user
        self.auth_session_service.revoke_auth_sessions_by_user_id(user_id=str(current_active_user.id))  # type: ignore

        return updated_user

    def revoke_user_tokens(self, *, user_id: str) -> TokensRevokedResponseSchema:
        """Revoke a user's access and refresh tokens.

        Args:
            user_id (str): The id of the user to revoke their tokens.

        Returns:
            TokensRevokedResponseSchema: The response after revoking tokens.
        """
        # get user object
        user = self.user_service.get_by_id(entity_id=user_id)

        # invalidate access token
        user.token_version += 1  # type: ignore

        self._persist_user_and_revoke(user=user, reason=RefreshTokenRevocationReasons.MANUAL_ADMIN_REVOKE.value)

        # revoke all auth sessions for user
        self.auth_session_service.revoke_auth_sessions_by_user_id(user_id=str(user.id))  # type: ignore

        return TokensRevokedResponseSchema(email=str(user.email), revoked=True)

    def suspend_user_account(self, *, user_id: str) -> AccountSuspendedResponseSchema:
        """Suspend a user account.

        Args:
            user_id (str): The id of the user to suspend.

        Returns:
            AccountSuspendedResponseSchema: The response after suspending account.
        """
        # get the user object
        user = self.user_service.get_by_id(entity_id=user_id)

        # set is suspended to true
        user.is_suspended = True  # type: ignore

        # revoke the access tokens
        user.token_version += 1  # type: ignore

        # save the user and revoke all access tokens
        self._persist_user_and_revoke(user=user, reason=RefreshTokenRevocationReasons.MANUAL_ADMIN_REVOKE.value)

        # revoke all auth sessions for user
        self.auth_session_service.revoke_auth_sessions_by_user_id(user_id=str(user.id))  # type: ignore

        return AccountSuspendedResponseSchema(email=str(user.email), is_suspended=bool(user.is_suspended))

    def reactivate_user_account(self, user_id: str) -> AccountSuspendedResponseSchema:
        """Reactivate a suspended user's account.

        Args:
            user_id (str): The id of the user account to reactivate.

        Returns:
            AccountSuspendedResponseSchema: The response after reactivating.
        """
        # get the user object
        user = self.user_service.get_by_id(entity_id=user_id)

        # reactivate user account by setting is suspended to false
        user.is_suspended = False  # type: ignore

        self._save_user(user=user)

        return AccountSuspendedResponseSchema(email=str(user.email), is_suspended=bool(user.is_suspended))

    def update_user_role(self, user_id: str, role_data: UpdateUserRoleSchema) -> User:
        """Update a user's roles.

        Args:
            user_id (str): The user to update their roles.
            role_data (UpdateUserRoleSchema): The role data to update the user's role with.

        Returns:
            User: The update user object.
        """
        # get roles
        roles = [self.role_service.get_by_id(entity_id=role_id) for role_id in role_data.role_ids]

        # get the user
        user = self.user_service.get_by_id(entity_id=user_id)

        # set user roles to the retrieved roles
        user.roles = roles

        # save the user and return it.
        updated_user = self._save_user(user=user)

        return updated_user

    def switch_user_role(
        self,
        *,
        current_user: User,
        data: SwitchRoleSchema,
        application: Application,
        device_id: str,
        client_type: Literal["web", "mobile", "api", "desktop", "cli"] = "web",
    ) -> dict:
        """Switch the active role of the user.

        Args:
            current_user (User): The current logged-in user.
            data (SwitchRoleSchema): The role data to switch to.
            application (Application): The application making the request.
            device_id (str): The device ID of the user.
            client_type (str): The client type of the user.

        Returns:
            dict: The response after switching roles.
        """
        # get the allowed user roles for the application making the request, if not found return None
        allowed_roles = INTERNAL_APPLICATION_ALLOWED_ROLES.get(str(application.app_name), None)

        # check if role exists
        role = self.role_service.get_by_id(entity_id=data.role_id)

        # check if the user has the role, if the role is allowed for the application making the request
        if role not in current_user.roles or not allowed_roles or role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.UNAUTHORIZED_USER.value,
            )

        auth_session = self._get_or_update_auth_session(
            user_id=str(current_user.id),
            device_id=device_id,
            client_type=client_type,
        )

        tokens = self._issue_tokens_and_refresh(
            user=current_user,
            active_role=str(role.name),
            auth_session=auth_session,
            reason=RefreshTokenRevocationReasons.MANUAL_ADMIN_REVOKE.value,
        )
        return {"token_type": "bearer", "access_token": tokens.access_token, "refresh_token": tokens.refresh_token}

    def _validate_roles(self, *, role_ids: list[str]) -> None:
        """Validate if roles exist.

        Args:
            role_ids (list[str]): List of role IDs to validate.
        """
        for role_id in role_ids:
            _ = self.role_service.get_by_id(entity_id=role_id)

    async def _send_verification_email(
        self,
        *,
        user: User,
        app_platform: Optional[str] = None,
        app_name: Optional[str] = None,
    ) -> None:
        """Generate token, build email, and send verification message.

        Args:
            user (User): The user to send the verification email to.
            app_platform (Optional[str]): The platform the request came from.
            (e.g. web, mobile)
            app_name (Optional[str]): The name of the application the request came from
        """
        token = self.token_service.create_token(
            payload={"sub": user.id, "iss": ApplicationConstants.APP_NAME.value},
            expires_in_minutes=auth_config.VERIFICATION_LINK_EXPIRES_IN_MINUTES,
            token_type=TokenTypeConstants.ACCOUNT_VERIFICATION_TOKEN.value,
        )

        verification_link = f"{project_config.FRONTEND_URL}/auth/verify-account?token={token}"

        # if app_platform attach to verification link
        if app_platform:
            verification_link = verification_link + f"&app_platform={app_platform}"

        # if app_name attach to verification link
        if app_name:
            verification_link = verification_link + f"&app_name={app_name}"

        body = AccountVerificationTemplateBodySchema(
            app_name=ApplicationConstants.APP_NAME.value,
            first_name="User",
            title="User Account Verification",
            code_expires_in_hours=24,
            current_year=datetime.now(tz=timezone.utc).year,
            verification_url=verification_link,
        ).model_dump()

        message = EmailNotificationMessageSchema(
            notification_type="account_verification",
            subject="Account Creation",
            recipients=[str(user.email)],
            template_name="account_creation.html",
            body=body,
        )
        await asyncio.to_thread(self.notification_publisher.publish_email_notification, message=message)

    @staticmethod
    def _get_current_user_active_role(*, user: User, application: Application) -> str | None:
        """Get the current active role of the user.

        Args:
            user (User): The user to get the active role for.
            application (Application): The application making the request.

        Returns:
            str: The active role of the user.
        """
        user_active_role = None

        # get the allowed user roles for the application making the request, if not found return None
        allowed_roles = INTERNAL_APPLICATION_ALLOWED_ROLES.get(str(application.app_name), None)

        # get intersection of application roles and user roles
        user_roles = {role.name for role in user.roles}
        user_application_roles = user_roles.intersection(allowed_roles) if allowed_roles else None

        if user_application_roles:
            # loop through the allowed roles and set the first found role as active role
            for role in allowed_roles:  # type: ignore
                if role in user_application_roles:
                    user_active_role = role
                    break

        return user_active_role

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
