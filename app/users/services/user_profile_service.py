from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.users.models import UserProfile
from app.users.repositories.user_profile_repository import UserProfileRepository
from app.users.schemas.request.user_profile import (
    CreateUserProfileSchema,
    UpdateUserProfileSchema,
)


class UserProfileService(BaseService[UserProfile]):
    """The service class for 'user_profile'."""

    def __init__(self, *, user_profile_repository: UserProfileRepository) -> None:
        """Initializer for 'user_profile' service.

        Args:
            user_profile_repository (UserProfileRepository): The user_profile repository.
        """
        self.user_profile_repository = user_profile_repository
        super().__init__(main_repository=user_profile_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[UserProfile]:
        """Get all user_profile entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[UserProfile]: A list of all entity instances
        """
        raise NotImplementedError

    def create(self, *, user_profile_data: CreateUserProfileSchema) -> UserProfile:
        """Create a new user_profile.

        Args:
            user_profile_data (CreateUserProfileSchema): The user_profile data to create.

        Returns:
            UserProfile: The newly created user_profile.
        """
        return self._default_create(
            entity_schema=user_profile_data,
            unique_field_to_check="user_id",
            unique_field_value=user_profile_data.user_id,
        )

    def update(self, *, user_id: str, data_to_update: UpdateUserProfileSchema) -> UserProfile:
        """Update a user profile.

        Args:
            user_id (str): The user to update their profile.
            data_to_update (UpdateUserProfileSchema): The data to update the user profile with.

        Returns:
            UserProfile: The updated user profile.
        """
        try:
            user_profile = self.get_by_field(field_name="user_id", value=user_id)
            return self.user_profile_repository.update(entity=user_profile, update_data=data_to_update.model_dump())  # type: ignore
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
