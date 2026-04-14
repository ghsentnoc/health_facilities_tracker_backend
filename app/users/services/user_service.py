from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from fastapi_mail.errors import ConnectionErrors

from app.auth.config.auth_config import auth_config
from app.auth.models import Role
from app.auth.schemas.mail_body import AccountVerificationTemplateBodySchema
from app.auth.services.token_service import TokenService
from app.auth.utils.constants import RoleConstants, TokenTypeConstants
from app.auth.utils.hash_password import PasswordHashManager
from app.core.config.project_config import project_config
from app.core.custom_exceptions import FacilityNotApprovedError
from app.core.services.base_service import BaseService
from app.core.services.mail_service import MailServiceBuilder
from app.core.utils.constants import ApplicationConstants
from app.core.utils.messages import ErrorMessages
from app.locations.models import Facility
from app.users.models import User, UserProfile
from app.users.repositories import UserRepository
from app.users.schemas.request.user import CreateFacilityRepSchema, CreateUserByAdminSchema, CreateUserSchema
from app.users.schemas.request.user_facility_association import CreateUserFacilityAssociationSchema
from app.users.schemas.request.user_profile import CreateUserProfileSchema
from app.users.services import UserFacilityAssociationService
from app.users.utils.allowed_filters_sort import (
    allowed_user_filters,
    allowed_user_sorts,
    user_filters_with_joins,
    user_filters_without_joins,
)


class UserService(BaseService[User]):
    """The service class for 'user'."""

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        user_profile_service: BaseService[UserProfile],
        user_facility_association_service: UserFacilityAssociationService,
        facility_service: BaseService[Facility],
        role_service: BaseService[Role],
        password_hash_manager: PasswordHashManager,
        mail_service: MailServiceBuilder,
        token_service: TokenService,
    ) -> None:
        """Initializer for 'user' service.

        Args:
            user_repository (UserRepository): The user repository.
            user_profile_service (BaseService[UserProfile]): The user profile service.
            user_facility_association_service (UserFacilityAssociationServoce): \
                The user facility association service.
            facility_service (BaseService[Facility]): The facility service.
            role_service (BaseService[Role]): The role service.
            password_hash_manager (PasswordHashManager): The password hash manager.
            mail_service (MailServiceBuilder): The mail service builder.
            token_service (TokenService): The token service.
        """
        self.user_repository = user_repository
        self.user_profile_service = user_profile_service
        self.user_facility_association_service = user_facility_association_service
        self.facility_service = facility_service
        self.role_service = role_service
        self.password_hash_manager = password_hash_manager
        self.mail_service = mail_service
        self.token_service = token_service
        super().__init__(main_repository=user_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[User]:
        """Get all user entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[User]: A list of all entity instances
        """
        return self._default_get_all(
            filters_with_joins=user_filters_with_joins,
            filters_without_joins=user_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_user_filters,
            allowed_sorts=allowed_user_sorts,
        )

    async def register_as_facility_representative(self, *, user_data: CreateFacilityRepSchema) -> User:
        """Register a user as a facility representative.

        Args:
            user_data (CreateFacilityRepSchema): The data to register the user with.

        Returns:
            User: The registered user.
        """
        # get the role of facility representative.
        facility_rep_role = self.role_service.get_by_field(
            field_name="name", value=RoleConstants.FACILITY_REP.value, operator="eq"
        )

        # hash the password
        hashed_password = self.password_hash_manager.hash_password(password=user_data.password)

        # build the user schema for creation
        new_user_schema = CreateUserSchema(email=user_data.email, password_hash=hashed_password)

        # create user and user profile
        user, user_profile = self._create_user_and_profile(
            user_data=new_user_schema, user_profile_data=user_data.user_profile.model_dump()
        )
        print(user, user_profile)

        # assign roles to user
        self._assign_roles(user=user, roles=[facility_rep_role])  # type: ignore

        # associate user to facility
        self._associate_user_to_facility(user_id=str(user.id), facility_id=user_data.facility_info.facility_id)

        # send verification email
        await self._send_verification_email(user=user, user_profile=user_profile)

        return user

    async def register_user_by_admin(self, *, user_data: CreateUserByAdminSchema) -> User:
        """Register a user by an admin.

        Args:
            user_data (CreateUserByAdminSchema): The data to register the user with.

        Returns:
            User: The registered user.
        """
        roles = self._get_roles(role_ids=user_data.role_ids)

        # build the user schema for creation
        new_user_schema = CreateUserSchema(email=user_data.email, password_hash=None)

        # create user and user profile
        user, user_profile = self._create_user_and_profile(
            user_data=new_user_schema, user_profile_data=user_data.user_profile.model_dump()
        )

        # assign roles to user
        self._assign_roles(user=user, roles=roles)

        # create user facility association if any
        if user_data.facility_info:
            self._associate_user_to_facility(user_id=str(user.id), facility_id=user_data.facility_info.facility_id)

        # send verification email
        await self._send_verification_email(user=user, user_profile=user_profile)
        return user

    def approve_facility_representative(self, *, user_id: str) -> User:
        """Approve a facility representative.

        Args:
            user_id (str): The user id of the facility representative.

        Returns:
            User: The returned user.
        """
        user = self.get_by_id(entity_id=user_id)

        if user.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.already_approved(object_type=User, value=str(user.email)),
            )

        approved_user = self.user_repository.approve_user(user_id=user_id)

        if not approved_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=User, value=str(user_id)),
            )

        return approved_user

    def _get_roles(self, *, role_ids: list[str]) -> list[Role]:
        """Get roles by their IDs.

        Args:
            role_ids (list[str]): The list of role ids to get.

        Returns:
            Role: The retrieved role.
        """
        roles = []
        for role_id in role_ids:
            role = self.role_service.get_by_id(entity_id=role_id)
            roles.append(role)
        return roles

    async def _send_verification_email(self, *, user: User, user_profile: UserProfile) -> None:
        """Send a verification email to user after registering account.

        Args:
            user (User): The user object.
            user_profile (UserProfile): The user profile object.
        """
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

    def _associate_user_to_facility(self, *, user_id: str, facility_id: str) -> None:
        """Associate a user to a facility.

        Args:
            user_id (str): The id of the user to associate to a facility.
            facility_id (str): The id of the facility to associate user to.
        """
        # check if facility exist.:
        user_facility = self.facility_service.get_by_id(entity_id=facility_id)

        # check if facility is approved.
        if not user_facility.is_approved:
            raise FacilityNotApprovedError(
                ErrorMessages.entity_not_approved(object_type=Facility, value=str(user_facility.name))
            )

        # check the number of users associated with the facility
        # if it's 4, raise an error since a facility can only have 4 representatives at max
        _ = self.user_facility_association_service.check_number_of_users_associated_with_facility(
            facility_id=str(user_facility.id)
        )

        # create association between user and facility
        self.user_facility_association_service.create(
            user_facility_association_data=CreateUserFacilityAssociationSchema(
                user_id=str(user_id), facility_id=str(user_facility.id)
            )
        )

    def _create_user_and_profile(
        self, *, user_data: CreateUserSchema, user_profile_data: dict
    ) -> tuple[User, UserProfile]:
        """Create user and user profile.

        Args:
            user_data (CreateUserSchema): The user data to create the user.
            user_profile_data (dict): The user profile data to create the profile for user.

        Returns:
            tuple[User, UserProfile]: The created user and user profile objects
        """
        # create user
        user = self._default_create(
            entity_schema=user_data, unique_field_to_check="email", unique_field_value=str(user_data.email)
        )

        # build user profile schema
        user_profile_schema = CreateUserProfileSchema(**user_profile_data, user_id=str(user.id))

        # create user profile
        user_profile = self.user_profile_service.create(user_profile_data=user_profile_schema)

        return user, user_profile

    def _assign_roles(self, *, user: User, roles: list[Role]) -> None:
        """Assign roles to a user.

        Args:
            user (User): The user to assign the roles to.
            roles (list[Role]): The list of roles to assign to user.
        """
        # add role to user
        user.roles = roles

        # commit the user with the role
        self.user_repository.save(object_to_save=user)

    def create(self, *args, **kwargs) -> User:  # type: ignore
        """Create a new user."""
        raise NotImplementedError

    def update(self, *args, **kwargs) -> User:  # type: ignore
        """Update an existing entity."""
        raise NotImplementedError
