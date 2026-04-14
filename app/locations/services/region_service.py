from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.locations.models import Region
from app.locations.repositories.region_repository import RegionRepository
from app.locations.schemas.request.region import CreateRegionSchema, UpdateRegionSchema
from app.locations.utils.allowed_filters_sort import (
    allowed_region_filters,
    allowed_region_sorts,
    region_filters_without_joins,
)


class RegionService(BaseService[Region]):
    """The service class for 'region'."""

    def __init__(self, *, region_repository: RegionRepository) -> None:
        """Initializer for 'region' service.

        Args:
            region_repository (RegionRepository): The region repository.
        """
        self.region_repository = region_repository
        super().__init__(main_repository=region_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[Region]:
        """Get all region entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Region]: A list of all entity instances
        """
        return self._default_get_all(
            filters_without_joins=region_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_region_filters,
            allowed_sorts=allowed_region_sorts,
        )

    def create(self, *, region_data: CreateRegionSchema) -> Region:
        """Create a new region.

        Args:
            region_data (CreateRegionSchema): The region data to create.

        Returns:
            Region: The newly created region.
        """
        return self._default_create(
            entity_schema=region_data, unique_field_to_check="name", unique_field_value=region_data.name
        )

    def update(self, *, region_id: str, data_to_update: UpdateRegionSchema) -> Region:
        """Update a region.

        Args:
            region_id (str): The id of the region to update.
            data_to_update (UpdateRegionSchema): The data to update the region with.

        Returns:
            Region: The updated region.
        """
        # check if region exists.
        region = self.get_by_id(entity_id=region_id)

        try:
            updated_region = self.region_repository.update(entity=region, update_data=data_to_update.model_dump())
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return updated_region
