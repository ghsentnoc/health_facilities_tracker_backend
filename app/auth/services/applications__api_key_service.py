import json
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.auth.models import APIKey, Application
from app.auth.repositories.applications__api_key_repository import (
    APIKeyRepository,
    ApplicationRepository,
)
from app.auth.schemas.request.applications_api_key import (
    CreateAPIKeySchema,
    CreateApplicationRequestSchema,
    CreateApplicationSchema,
    UpdateAPIKeySchema,
    UpdateApplicationSchema,
)
from app.auth.utils.allowed_filters_sort import (
    allowed_application_api_key_filters,
    allowed_application_api_key_sorts,
    allowed_application_registration_filters,
    allowed_application_registration_sorts,
    application_api_key_filters_without_joins,
    application_api_keys_filters_with_joins,
    application_registration_filters_without_joins,
)
from app.auth.utils.constants import APIKeyRevocationReasonConstants
from app.auth.utils.hash_password import PasswordHashManager
from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_uuid
from app.users.models import User


class APIKeyService(BaseService[APIKey]):
    """Service for managing APIKey entities.

    The API key creation enforces uniqueness on the combination of
    ``api_key_id`` and ``application_id`` to avoid duplicate keys for the same
    application.
    """

    def __init__(self, *, api_key_repository: APIKeyRepository, hash_manager: PasswordHashManager) -> None:
        """Initialize the service.

        Args:
            hash_manager (PasswordHashManager): The hash manager.
            api_key_repository (APIKeyRepository): Repository used for APIKey persistence operations.
        """
        self.api_key_repository = api_key_repository
        self.hash_manager = hash_manager
        super().__init__(main_repository=api_key_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[APIKey]:
        """Return a list of API keys matching query params.

        Args:
            pagination: Optional pagination query string.
            filters: Optional filters query string.
            sort: Optional sort query string.

        Returns:
            List of ``APIKey`` instances.
        """
        return self._default_get_all(
            filters_without_joins=application_api_key_filters_without_joins,
            filters_with_joins=application_api_keys_filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_application_api_key_filters,
            allowed_sorts=allowed_application_api_key_sorts,
        )

    def create(self, *, api_key_data: CreateAPIKeySchema) -> APIKey:
        """Create a new API key.

        The service enforces the uniqueness of ``api_key_id`` for the same
        ``application_id`` by checking both fields before creating.

        Args:
            api_key_data: Schema with API key creation data.

        Returns:
            The newly created ``APIKey`` instance.
        """
        return self._default_create(
            entity_schema=api_key_data,
            unique_field_to_check=["api_key_id"],
            unique_field_value={"api_key_id": api_key_data.api_key_id},
        )

    def update(self, *, api_key_id: str, data_to_update: UpdateAPIKeySchema) -> APIKey:
        """Update an existing API key.

        Args:
            api_key_id: ID of the API key (the model's `id` field) to update.
            data_to_update: Schema containing update values.

        Returns:
            The updated ``APIKey`` instance.

        Raises:
            HTTPException: If an update would create a duplicate entity.
        """
        # api_key = self.get_by_id(entity_id=api_key_id)
        #
        # try:
        #     return self.api_key_repository.update(entity=api_key, update_data=data_to_update.model_dump())
        # except ObjectAlreadyExistsException as e:
        #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
        raise NotImplementedError

    def revoke_api_keys(
        self,
        *,
        application_id: str,
        reason: str,
        new_api_key_id: Optional[str] = None,
    ) -> None:
        """Revoke API keys matching the provided filters.

        This method mirrors the revocation behaviour in the refresh token service.

        Args:
            application_id: If provided, revoke all non-revoked keys for this application.
            reason: Reason for revocation.
            new_api_key_id: Optional API key identifier that replaced the revoked keys.

        Raises:
            HTTPException: If neither `application_id` nor `api_key_id` is provided.
        """
        if not is_valid_uuid(uuid_to_test=application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Application, value=application_id),
            )

        # check if the application exists
        application = self.api_key_repository.db_session.query(Application).filter_by(id=application_id).first()

        if application.is_deleted or not application:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Application, value=application_id),
            )

        # Build filters to fetch non-revoked API keys for the given criteria
        filters: dict = {"revoked": {"value": False}, "application_id": {"value": application_id, "operator": "eq"}}

        api_keys = self.get_all(filters=json.dumps(filters))

        for key in api_keys:
            update_data = {
                "revoked": True,
                "revoked_at": datetime.now(tz=timezone.utc),
                "replaced_by_api_key": new_api_key_id,
                "revoked_reason": reason,
                "last_used_at": None,
            }

            # Use repository update directly with a dict
            self.api_key_repository.update(entity=key, update_data=update_data)

    def rotate_api_key(
        self,
        *,
        application_id: str,
        reason: str = APIKeyRevocationReasonConstants.ROTATION.value,
        number_of_bytes: int = 24,
        current_user: User,
    ) -> str:
        """Rotate the API key for an application and revoke previous keys.

        Generates a brand-new API key for the application (or the application
        associated with the provided `api_key_id`), stores the hashed value in
        the database, then revokes all previously active (non-revoked) API keys
        for that application while marking them as replaced by the new key.

        The method returns the plaintext (unhashed) API key so it can be
        delivered to the caller. The plaintext consists of the secret and the
        generated api_key_id joined by a dot ("<secret>.<api_key_id>").

        Args:
            application_id: The id of the application to rotate keys for. If
                omitted, `api_key_id` must be provided and will be used to
                determine the application.
            reason: Textual reason for rotation (stored on revoked keys).
            number_of_bytes: Number of random bytes used to generate the secret
            current_user (User): The current logged-in user.

        Returns:
            str: The plaintext new API key (secret + "." + api_key_id).

        Raises:
            HTTPException: If neither `application_id` nor `api_key_id` is
                provided, or if `api_key_id` is provided but not found.
        """
        if not is_valid_uuid(uuid_to_test=application_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Application, value=application_id),
            )

        # check if the application exists
        application = self.api_key_repository.db_session.query(Application).filter_by(id=application_id).first()

        if application.is_deleted or not application:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Application, value=application_id),
            )

        if not application.is_active:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.INACTIVE_APPLICATION.value
            )

        # check if user is authorized to rotate the keys of application
        if current_user.id != application.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.UNAUTHORIZED_USER.value)

        # get api_keys for application
        existing_keys = self.get_by_field(field_name="application_id", value=application_id, operator="eq")

        # generate new key and persist it
        secret_key, new_api_key_id, plain_text = self.generate_api_key(number_of_bytes=number_of_bytes)
        hashed_api_key = self.hash_manager.hash_password(password=secret_key)

        if existing_keys:
            # revoke all tokens for that application
            self.revoke_api_keys(application_id=application_id, reason=reason, new_api_key_id=new_api_key_id)

        # create the new APIKey record
        _ = self.create(
            api_key_data=CreateAPIKeySchema(
                application_id=application_id,  # type: ignore[arg-type]
                api_key_id=new_api_key_id,
                api_key_hash=hashed_api_key,
            )
        )

        # return plaintext so callers can display/deliver it once
        return plain_text

    @staticmethod
    def generate_api_key(number_of_bytes: int = 24) -> tuple[str, str, str]:
        """Generate the api_key.

        Args:
            number_of_bytes (int): The number of bytes for secret key.

        Returns:
            str: The generated api key.
        """
        secret_key = secrets.token_hex(nbytes=number_of_bytes)
        api_key_id = str(uuid.uuid4())
        plain_text = secret_key + "." + api_key_id

        return secret_key, api_key_id, plain_text


class ApplicationService(BaseService[Application]):
    """Service for managing Application entities.

    This service delegates database operations to an ``ApplicationRepository`` and
    uses helpers from ``BaseService`` for common behaviours (pagination, create
    with uniqueness checks, get-by-id, delete/restore, etc.).
    """

    def __init__(
        self,
        *,
        application_repository: ApplicationRepository,
        api_key_service: APIKeyService,
        hash_manager: PasswordHashManager,
    ) -> None:
        """Initialize the service.

        Args:
            application_repository (ApplicationRepository): Repository used for
                Application persistence operations.
            api_key_service (APIKeyService): The api key service
            hash_manager (PasswordHashManager): The hash manager to hash keys
        """
        self.application_repository = application_repository
        self.api_key_service = api_key_service
        self.hash_manager = hash_manager
        super().__init__(main_repository=application_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[Application]:
        """Return a list of applications matching query params.

        Args:
            pagination: Optional pagination query string.
            filters: Optional filters query string.
            sort: Optional sort query string.

        Returns:
            List of ``Application`` instances.
        """
        return self._default_get_all(
            filters_without_joins=application_registration_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_application_registration_filters,
            allowed_sorts=allowed_application_registration_sorts,
        )

    def create(  # type: ignore
        self, *, current_user: User, application_data: CreateApplicationRequestSchema
    ) -> tuple[Application, str]:
        """Create a new application.

        Ensures an application with the same ``app_name`` does not already exist
        (including soft-deleted ones).

        Args:
            current_user (User): The user registering the application.
            application_data: Schema with application creation data.

        Returns:
            The newly created ``Application`` instance.

        Raises:
            HTTPException: If an application with the same name already exists.
        """
        # if current user is none raise error
        if not current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.UNAUTHORIZED_USER.value)

        # create application request schema
        _application_data = CreateApplicationSchema(**application_data.model_dump(), user_id=current_user.id)  # type: ignore

        # create the application if not exists then create the api key for that application
        application = self._default_create(
            entity_schema=_application_data,
            unique_field_to_check="app_name",
            unique_field_value=application_data.app_name,
        )

        # generate the api key
        secret_key, api_key_id, plain_text = APIKeyService.generate_api_key(number_of_bytes=24)

        # hash the api key
        hashed_api_key = self.hash_manager.hash_password(password=secret_key)

        # create the api key for application
        _ = self.api_key_service.create(
            api_key_data=CreateAPIKeySchema(
                application_id=str(application.id), api_key_id=api_key_id, api_key_hash=hashed_api_key
            )
        )

        # add application_id and api_key to application object
        application.api_key = plain_text  # type: ignore

        return application, plain_text

    def update(self, *, application_id: str, data_to_update: UpdateApplicationSchema) -> Application:
        """Update an existing application.

        Args:
            application_id: ID of the application to update.
            data_to_update: Schema containing update values.

        Returns:
            The updated ``Application`` instance.

        Raises:
            HTTPException: If an update would create a duplicate entity.
        """
        application = self.get_by_id(entity_id=application_id)

        try:
            return self.application_repository.update(entity=application, update_data=data_to_update.model_dump())
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    def deactivate_application(self, *, application_id: str) -> Application:
        """Deactivate an application.

        Args:
            application_id (str): The id of the application to deactivate.

        Returns:
            Application: The deactivated application.
        """
        # get the application
        application = self.get_by_id(entity_id=application_id)

        # set the is_active value to False
        if not application.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.ALREADY_DEACTIVATED.value)

        application.is_active = False  # type: ignore

        # revoke all application tokens
        self.api_key_service.revoke_api_keys(
            application_id=application_id, reason=APIKeyRevocationReasonConstants.APPLICATION_DEACTIVATED.value
        )

        return self.application_repository.save(object_to_save=application)

    def activate_application(self, *, application_id: str) -> tuple[Application, str]:
        """Deactivate an application.

        Args:
            application_id (str): The id of the application to deactivate.

        Returns:
            Application: The deactivated application.
        """
        # get the application
        application = self.get_by_id(entity_id=application_id)

        if application.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMessages.ALREADY_ACTIVATED.value)

        # set the is_active value to True
        application.is_active = True  # type: ignore

        # create new token
        # generate the api key
        secret_key, api_key_id, plain_text = APIKeyService.generate_api_key(number_of_bytes=24)

        # hash the api key
        hashed_api_key = self.hash_manager.hash_password(password=secret_key)

        # create the api key for application
        _ = self.api_key_service.create(
            api_key_data=CreateAPIKeySchema(
                application_id=application.id,  # type: ignore
                api_key_id=api_key_id,
                api_key_hash=hashed_api_key,
            )
        )

        # add application_id and api_key to application object
        application.api_key = plain_text  # type: ignore

        return self.application_repository.save(object_to_save=application), plain_text

    def delete(self, *, entity_id: str) -> Application:
        """Delete an application.

        Args:
            entity_id (str): The application id.

        Returns:
            Application: The deleted application.
        """
        # revoke all tokens
        self.api_key_service.revoke_api_keys(
            application_id=entity_id, reason=APIKeyRevocationReasonConstants.APPLICATION_DELETED.value
        )

        return self._default_delete(entity_id=entity_id)
