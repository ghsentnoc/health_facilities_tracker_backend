from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.core.utils.messages import ErrorMessages
from app.locations.models import District, Facility, FacilityContact
from app.locations.repositories import FacilityContactRepository, FacilityRepository
from app.locations.schemas.request.facility import (
    CreateFacilityRequestSchema,
    UpdateFacilityRequestSchema,
)
from app.locations.utils.allowed_filters_sort import (
    allowed_facility_filters,
    allowed_facility_sorts,
    facility_filters_with_joins,
    facility_filters_without_joins,
)


class FacilityService(BaseService[Facility]):
    """The service class for 'facility'."""

    def __init__(
        self,
        *,
        facility_repository: FacilityRepository,
        facility_contact_repository: FacilityContactRepository,
        district_service: BaseService[District],
    ) -> None:
        """Initializer for 'facility' service.

        Args:
            facility_repository (FacilityRepository): The facility repository.
            facility_contact_repository (FacilityContactRepository): The facility contact repository.
            district_service (BaseService[District]): The district service.
        """
        self.facility_repository = facility_repository
        self.facility_contact_repository = facility_contact_repository
        self.district_service = district_service
        super().__init__(main_repository=facility_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[Facility]:
        """Get all facility entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Facility]: A list of all entity instances
        """
        return self._default_get_all(
            filters_with_joins=facility_filters_with_joins,
            filters_without_joins=facility_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_facility_filters,
            allowed_sorts=allowed_facility_sorts,
        )

    def create(self, *, facility_data: CreateFacilityRequestSchema) -> Facility:
        """Create a new facility.

        Args:
            facility_data (CreateFacilitySchema): The facility data to create.

        Returns:
            Facility: The newly created facility.
        """
        # check if district exists.
        _ = self.district_service.get_by_id(entity_id=facility_data.district_id)

        try:
            facility = self.facility_repository.create(data=facility_data.model_dump(exclude={"contact_numbers"}))
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        # create facility contact numbers
        if facility_data.contact_numbers:
            for contact_number in facility_data.contact_numbers:
                self.facility_contact_repository.create(
                    data={"facility_id": facility.id, "contact_number": contact_number}
                )

        return facility

    def update(self, *, facility_id: str, data_to_update: UpdateFacilityRequestSchema) -> Facility:
        """Update a facility.

        Args:
            facility_id (str): The id of the facility to update.
            data_to_update (UpdateFacilitySchema): The data to update the facility with.

        Returns:
            Facility: The updated facility.
        """
        # check if facility exists.
        facility = self.get_by_id(entity_id=facility_id)
        _ = self.district_service.get_by_id(entity_id=data_to_update.district_id)

        try:
            updated_facility = self.facility_repository.update(
                entity=facility, update_data=data_to_update.model_dump(exclude={"contact_numbers"})
            )

            # update facility contact numbers
            if data_to_update.contact_numbers is not None:
                existing_contact_numbers = {
                    str(contact.contact_number)
                    for contact in self.facility_contact_repository.db_session.query(FacilityContact)
                    .filter(
                        FacilityContact.facility_id == facility_id,
                        FacilityContact.is_deleted.is_(False),
                    )
                    .all()
                }
                requested_contact_numbers = set(data_to_update.contact_numbers)

                for contact_number in requested_contact_numbers - existing_contact_numbers:
                    self.facility_contact_repository.create(
                        data={"facility_id": facility_id, "contact_number": contact_number}
                    )

                for contact_number in existing_contact_numbers - requested_contact_numbers:
                    self.facility_contact_repository.delete_contact_number_for_facility(
                        contact_number=contact_number, facility_id=facility_id
                    )

        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return updated_facility

    def approve_facility(self, *, facility_id: str) -> Facility:
        """Approve a facility.

        Args:
            facility_id (str): The id of the facility to approve.

        Returns:
            Facility: The approved facility.
        """
        facility = self.get_by_id(entity_id=facility_id)

        if facility.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.already_approved(object_type=Facility, value=str(facility.name)),
            )

        approved_facility = self.facility_repository.approve_facility(facility_id=facility_id)

        if not approved_facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Facility, value=str(facility_id)),
            )
        return approved_facility

    def license_facility(self, *, facility_id: str) -> Facility:
        """License a facility.

        Args:
            facility_id (str): The id of the facility to license.

        Returns:
            Facility: The licensed facility.
        """
        facility = self.get_by_id(entity_id=facility_id)

        if facility.is_licensed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.already_licensed(object_type=Facility, value=str(facility.name)),
            )

        licensed_facility = self.facility_repository.license_facility(facility_id=facility_id)

        if not licensed_facility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Facility, value=str(facility_id)),
            )
        return licensed_facility
