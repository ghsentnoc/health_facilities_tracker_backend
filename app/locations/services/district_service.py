from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.locations.models import District, Region
from app.locations.repositories.district_repository import DistrictRepository
from app.locations.schemas.request.district import CreateDistrictSchema, UpdateDistrictSchema
from app.locations.utils.allowed_filters_sort import (
    allowed_district_filters,
    allowed_district_sorts,
    district_filters_with_joins,
    district_filters_without_joins,
)


class DistrictService(BaseService[District]):
    """The service class for 'district'."""

    def __init__(self, *, district_repository: DistrictRepository, region_service: BaseService[Region]) -> None:
        """Initializer for 'district' service.

        Args:
            district_repository (DistrictRepository): The district repository.
            region_service (BaseService[Region]): The region service.
        """
        self.district_repository = district_repository
        self.region_service = region_service
        super().__init__(main_repository=district_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[District]:
        """Get all district entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[District]: A list of all entity instances
        """
        return self._default_get_all(
            filters_with_joins=district_filters_with_joins,
            filters_without_joins=district_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_district_filters,
            allowed_sorts=allowed_district_sorts,
        )

    def create(self, *, district_data: CreateDistrictSchema) -> District:
        """Create a new district.

        Args:
            district_data (CreateDistrictSchema): The district data to create.

        Returns:
            District: The newly created district.
        """
        # check if region exists.
        _ = self.region_service.get_by_id(entity_id=district_data.region_id)

        return self._default_create(
            entity_schema=district_data, unique_field_to_check="name", unique_field_value=district_data.name
        )

    def update(self, *, district_id: str, data_to_update: UpdateDistrictSchema) -> District:
        """Update a district.

        Args:
            district_id (str): The id of the district to update.
            data_to_update (UpdateDistrictSchema): The data to update the district with.

        Returns:
            District: The updated district.
        """
        # check if district exists.
        district = self.get_by_id(entity_id=district_id)
        _ = self.region_service.get_by_id(entity_id=data_to_update.region_id)

        try:
            updated_district = self.district_repository.update(entity=district, update_data=data_to_update.model_dump())
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return updated_district
