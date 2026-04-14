from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.locations.dependencies.facility_service_dependency import create_facility_service
from app.locations.docs.facilities_docs import (
    create_facility_docs,
    delete_facility_docs,
    get_all_facilities_docs,
    get_facility_by_id_docs,
    restore_facility_docs,
    update_facility_docs,
)
from app.locations.models import Facility
from app.locations.schemas.request.facility import CreateFacilityRequestSchema, UpdateFacilityRequestSchema
from app.locations.schemas.response.facility import ReadFacilitySchema
from app.locations.services.facility_service import FacilityService

facility_router = APIRouter(prefix="/facilities", tags=["Facilities"], dependencies=[Depends(validate_api_key)])


@facility_router.post(path="", status_code=status.HTTP_201_CREATED, description=create_facility_docs)
def create_facility(
    request: Request,
    facility_data: CreateFacilityRequestSchema,
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling creating a new facility.

    Args:
        request (Request): The request object.
        facility_data (CreateFacilityRequestSchema): The data needed to create the facility.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.create(facility_data=facility_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@facility_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_facilities_docs)
def get_all_facilities(
    request: Request,
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all facilities request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    facilities = facility_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": facility_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(facilities)})

    response_facilities = [
        facility if isinstance(facility, dict) else ReadFacilitySchema(**facility.to_dict())  # type: ignore
        for facility in facilities
    ]

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Facility),  # type: ignore
        data=response_facilities,
        extras=extras,
        request=request,
    )

    return response_data


@facility_router.get(path="/{facility_id}", status_code=status.HTTP_200_OK, description=get_facility_by_id_docs)
def get_facility_by_id(
    request: Request,
    facility_id: Annotated[str, Path(..., description="The id of the facility to get.")],
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling get a facility by id request.

    Args:
        request (Request): The request object.
        facility_id (str): The id of the facility to retrieve.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.get_by_id(entity_id=facility_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@facility_router.put(path="/{facility_id}", status_code=status.HTTP_200_OK, description=update_facility_docs)
def update_facility(
    request: Request,
    facility_id: Annotated[str, Path(..., description="The id of the facility to get.")],
    data_to_update: UpdateFacilityRequestSchema,
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling update a facility by id request.

    Args:
        request (Request): The request object.
        facility_id (str): The id of the facility to update.
        data_to_update (UpdateFacilityRequestSchema): The data to update facility with.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.update(facility_id=facility_id, data_to_update=data_to_update)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@facility_router.patch(path="/{facility_id}/approve", status_code=status.HTTP_200_OK, description="Approve a facility.")
def approve_facility(
    request: Request,
    facility_id: Annotated[str, Path(..., description="The id of the facility to approve.")],
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling approve a facility by id request.

    Args:
        request (Request): The request object.
        facility_id (str): The id of the facility to approve.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.approve_facility(facility_id=facility_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.approved_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@facility_router.patch(path="/{facility_id}/license", status_code=status.HTTP_200_OK, description="License a facility.")
def license_facility(
    request: Request,
    facility_id: Annotated[str, Path(..., description="The id of the facility to license.")],
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling license a facility by id request.

    Args:
        request (Request): The request object.
        facility_id (str): The id of the facility to license.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.license_facility(facility_id=facility_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.licensed_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@facility_router.delete(path="/{facility_id}", status_code=status.HTTP_200_OK, description=delete_facility_docs)
def delete_facility(
    request: Request,
    facility_id: Annotated[str, Path(..., description="The id of the facility to get.")],
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling delete a facility by id request.

    Args:
        request (Request): The request object.
        facility_id (str): The id of the facility to delete.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.delete(entity_id=facility_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@facility_router.patch(path="/{facility_id}/restore", status_code=status.HTTP_200_OK, description=restore_facility_docs)
def restore_facility(
    request: Request,
    facility_id: Annotated[str, Path(..., description="The id of the facility to get.")],
    facility_service: Annotated[FacilityService, Depends(create_facility_service)],
) -> ResponseSchema:
    """Method for handling restore a facility by id request.

    Args:
        request (Request): The request object.
        facility_id (str): The id of the facility to restore.
        facility_service (FacilityService): The facility service to use.

    Returns:
        ResponseSchema: The response data.
    """
    facility = facility_service.restore(entity_id=facility_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=Facility),  # type: ignore
        data=ReadFacilitySchema(**facility.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
