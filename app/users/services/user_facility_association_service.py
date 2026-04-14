from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.core.utils.messages import ErrorMessages
from app.users.models import UserFacilityAssociation
from app.users.repositories.user_facility_association_repository import UserFacilityAssociationRepository
from app.users.schemas.request.user_facility_association import (
    CreateUserFacilityAssociationSchema,
    UpdateUserFacilityAssociationSchema,
)


class UserFacilityAssociationService(BaseService[UserFacilityAssociation]):
    """The service class for 'user_facility_association'."""

    MAXIMUM_NUMBER_OF_USERS_PER_FACILITY = 4

    def __init__(self, *, user_facility_association_repository: UserFacilityAssociationRepository) -> None:
        """Initializer for 'user_facility_association' service.

        Args:
            user_facility_association_repository (UserFacilityAssociationRepository): \
                The user_facility_association repository.
        """
        self.user_facility_association_repository = user_facility_association_repository
        super().__init__(main_repository=user_facility_association_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[UserFacilityAssociation]:
        """Get all user_facility_association entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[UserFacilityAssociation]: A list of all entity instances
        """
        raise NotImplementedError

    def create(self, *, user_facility_association_data: CreateUserFacilityAssociationSchema) -> UserFacilityAssociation:
        """Create a new user_facility_association.

        Args:
            user_facility_association_data (CreateUserFacilityAssociationSchema): \
                The user_facility_association data to create.

        Returns:
            UserFacilityAssociation: The newly created user_facility_association.
        """
        return self._default_create(
            entity_schema=user_facility_association_data,
            unique_field_to_check="user_id",
            unique_field_value=user_facility_association_data.user_id,
        )

    def update(self, *, user_id: str, data_to_update: UpdateUserFacilityAssociationSchema) -> UserFacilityAssociation:
        """Update a user facility association.

        Args:
            user_id (str): The user id of the facility association to update.
            data_to_update (UpdateUserFacilityAssociationSchema): The data to update the user facility association with.

        Returns:
            UserFacilityAssociation: The updated user facility association.
        """
        try:
            user_facility_association = self.get_by_field(field_name="user_id", value=user_id, operator="eq")
            return self.user_facility_association_repository.update(
                entity=user_facility_association,  # type: ignore
                update_data=data_to_update.model_dump(),
            )
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    def check_number_of_users_associated_with_facility(self, *, facility_id: str) -> int:
        """Check the number of users associated with a facility.

        Args:
            facility_id (str): The id of the facility to check.

        Returns:
            int: The number of users associated with the facility.

        Raises:
            HTTPException: If the number of users associated with the facility is 4 or more.
        """
        number_of_users = self.user_facility_association_repository.count_by_field(
            field_name="facility_id", value=facility_id
        )
        if number_of_users >= self.MAXIMUM_NUMBER_OF_USERS_PER_FACILITY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.FACILITY_REPRESENTATIVE_LIMIT_EXCEEDED.value,
            )
        return number_of_users
