from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.locations.dependencies.district_service_dependency import create_district_service
from app.locations.docs.districts_docs import (
    create_district_docs,
    delete_district_docs,
    get_all_districts_docs,
    get_district_by_id_docs,
    restore_district_docs,
    update_district_docs,
)
from app.locations.models import District
from app.locations.schemas.request.district import CreateDistrictSchema, UpdateDistrictSchema
from app.locations.schemas.response.district import ReadDistrictSchema
from app.locations.services.district_service import DistrictService

district_router = APIRouter(prefix="/districts", tags=["District"], dependencies=[Depends(validate_api_key)])


@district_router.post(path="", status_code=status.HTTP_201_CREATED, description=create_district_docs)
def create_district(
    request: Request,
    district_data: CreateDistrictSchema,
    district_service: Annotated[DistrictService, Depends(create_district_service)],
) -> ResponseSchema:
    """Method for handling creating a new district.

    Args:
        request (Request): The request object.
        district_data (CreateDistrictSchema): The data needed to create the district.
        district_service (DistrictService): The district service to use.

    Returns:
        ResponseSchema: The response data.
    """
    district = district_service.create(district_data=district_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=District),  # type: ignore
        data=ReadDistrictSchema(**district.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@district_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_districts_docs)
def get_all_districts(
    request: Request,
    district_service: Annotated[DistrictService, Depends(create_district_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all districts request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        district_service (DistrictService): The district service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    districts = district_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": district_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(districts)})

    response_districts = [
        district if isinstance(district, dict) else ReadDistrictSchema(**district.to_dict())  # type: ignore
        for district in districts
    ]

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=District),  # type: ignore
        data=response_districts,
        extras=extras,
        request=request,
    )

    return response_data


@district_router.get(path="/{district_id}", status_code=status.HTTP_200_OK, description=get_district_by_id_docs)
def get_district_by_id(
    request: Request,
    district_id: Annotated[str, Path(..., description="The id of the district to get.")],
    district_service: Annotated[DistrictService, Depends(create_district_service)],
) -> ResponseSchema:
    """Method for handling get a district by id request.

    Args:
        request (Request): The request object.
        district_id (str): The id of the district to retrieve.
        district_service (DistrictService): The district service to use.

    Returns:
        ResponseSchema: The response data.
    """
    district = district_service.get_by_id(entity_id=district_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=District),  # type: ignore
        data=ReadDistrictSchema(**district.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@district_router.put(path="/{district_id}", status_code=status.HTTP_200_OK, description=update_district_docs)
def update_district(
    request: Request,
    district_id: Annotated[str, Path(..., description="The id of the district to get.")],
    data_to_update: UpdateDistrictSchema,
    district_service: Annotated[DistrictService, Depends(create_district_service)],
) -> ResponseSchema:
    """Method for handling update a district by id request.

    Args:
        request (Request): The request object.
        district_id (str): The id of the district to update.
        data_to_update (UpdateDistrictSchema): The data to update district with.
        district_service (DistrictService): The district service to use.

    Returns:
        ResponseSchema: The response data.
    """
    district = district_service.update(district_id=district_id, data_to_update=data_to_update)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=District),  # type: ignore
        data=ReadDistrictSchema(**district.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@district_router.delete(path="/{district_id}", status_code=status.HTTP_200_OK, description=delete_district_docs)
def delete_district(
    request: Request,
    district_id: Annotated[str, Path(..., description="The id of the district to get.")],
    district_service: Annotated[DistrictService, Depends(create_district_service)],
) -> ResponseSchema:
    """Method for handling delete a district by id request.

    Args:
        request (Request): The request object.
        district_id (str): The id of the district to delete.
        district_service (DistrictService): The district service to use.

    Returns:
        ResponseSchema: The response data.
    """
    district = district_service.delete(entity_id=district_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=District),  # type: ignore
        data=ReadDistrictSchema(**district.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@district_router.patch(path="/{district_id}/restore", status_code=status.HTTP_200_OK, description=restore_district_docs)
def restore_district(
    request: Request,
    district_id: Annotated[str, Path(..., description="The id of the district to get.")],
    district_service: Annotated[DistrictService, Depends(create_district_service)],
) -> ResponseSchema:
    """Method for handling restore a district by id request.

    Args:
        request (Request): The request object.
        district_id (str): The id of the district to restore.
        district_service (DistrictService): The district service to use.

    Returns:
        ResponseSchema: The response data.
    """
    district = district_service.restore(entity_id=district_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=District),  # type: ignore
        data=ReadDistrictSchema(**district.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
