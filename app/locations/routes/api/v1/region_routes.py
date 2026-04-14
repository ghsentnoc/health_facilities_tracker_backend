from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.locations.dependencies.region_service_dependency import create_region_service
from app.locations.docs.regions_docs import (
    create_region_docs,
    delete_region_docs,
    get_all_regions_docs,
    get_region_by_id_docs,
    restore_region_docs,
    update_region_docs,
)
from app.locations.models import Region
from app.locations.schemas.request.region import CreateRegionSchema, UpdateRegionSchema
from app.locations.schemas.response.region import ReadRegionSchema
from app.locations.services.region_service import RegionService

region_router = APIRouter(prefix="/regions", tags=["Region"], dependencies=[Depends(validate_api_key)])


@region_router.post(path="", status_code=status.HTTP_201_CREATED, description=create_region_docs)
def create_region(
    request: Request,
    region_data: CreateRegionSchema,
    region_service: Annotated[RegionService, Depends(create_region_service)],
) -> ResponseSchema:
    """Method for handling creating a new region.

    Args:
        request (Request): The request object.
        region_data (CreateRegionSchema): The data needed to create the region.
        region_service (RegionService): The region service to use.

    Returns:
        ResponseSchema: The response data.
    """
    region = region_service.create(region_data=region_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Region),  # type: ignore
        data=ReadRegionSchema(**region.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@region_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_regions_docs)
def get_all_regions(
    request: Request,
    region_service: Annotated[RegionService, Depends(create_region_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all regions request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        region_service (RegionService): The region service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    regions = region_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": region_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(regions)})

    response_regions = [
        region if isinstance(region, dict) else ReadRegionSchema(**region.to_dict())  # type: ignore
        for region in regions
    ]

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Region),  # type: ignore
        data=response_regions,
        extras=extras,
        request=request,
    )

    return response_data


@region_router.get(path="/{region_id}", status_code=status.HTTP_200_OK, description=get_region_by_id_docs)
def get_region_by_id(
    request: Request,
    region_id: Annotated[str, Path(..., description="The id of the region to get.")],
    region_service: Annotated[RegionService, Depends(create_region_service)],
) -> ResponseSchema:
    """Method for handling get a region by id request.

    Args:
        request (Request): The request object.
        region_id (str): The id of the region to retrieve.
        region_service (RegionService): The region service to use.

    Returns:
        ResponseSchema: The response data.
    """
    region = region_service.get_by_id(entity_id=region_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Region),  # type: ignore
        data=ReadRegionSchema(**region.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@region_router.put(path="/{region_id}", status_code=status.HTTP_200_OK, description=update_region_docs)
def update_region(
    request: Request,
    region_id: Annotated[str, Path(..., description="The id of the region to get.")],
    data_to_update: UpdateRegionSchema,
    region_service: Annotated[RegionService, Depends(create_region_service)],
) -> ResponseSchema:
    """Method for handling update a region by id request.

    Args:
        request (Request): The request object.
        region_id (str): The id of the region to update.
        data_to_update (UpdateRegionSchema): The data to update region with.
        region_service (RegionService): The region service to use.

    Returns:
        ResponseSchema: The response data.
    """
    region = region_service.update(region_id=region_id, data_to_update=data_to_update)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=Region),  # type: ignore
        data=ReadRegionSchema(**region.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@region_router.delete(path="/{region_id}", status_code=status.HTTP_200_OK, description=delete_region_docs)
def delete_region(
    request: Request,
    region_id: Annotated[str, Path(..., description="The id of the region to get.")],
    region_service: Annotated[RegionService, Depends(create_region_service)],
) -> ResponseSchema:
    """Method for handling delete a region by id request.

    Args:
        request (Request): The request object.
        region_id (str): The id of the region to delete.
        region_service (RegionService): The region service to use.

    Returns:
        ResponseSchema: The response data.
    """
    region = region_service.delete(entity_id=region_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=Region),  # type: ignore
        data=ReadRegionSchema(**region.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@region_router.patch(path="/{region_id}/restore", status_code=status.HTTP_200_OK, description=restore_region_docs)
def restore_region(
    request: Request,
    region_id: Annotated[str, Path(..., description="The id of the region to get.")],
    region_service: Annotated[RegionService, Depends(create_region_service)],
) -> ResponseSchema:
    """Method for handling restore a region by id request.

    Args:
        request (Request): The request object.
        region_id (str): The id of the region to restore.
        region_service (RegionService): The region service to use.

    Returns:
        ResponseSchema: The response data.
    """
    region = region_service.restore(entity_id=region_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=Region),  # type: ignore
        data=ReadRegionSchema(**region.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
