from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from app.auth.dependencies.auth_dependency import get_current_user, validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.users.dependencies.user_facility_association_service_dependency import create_user_facility_association_service
from app.users.models import User, UserFacilityAssociation
from app.users.schemas.request.user_facility_association import UpdateUserFacilityAssociationSchema
from app.users.schemas.response.user_facility_association import ReadUserFacilityAssociationSchema
from app.users.services import UserFacilityAssociationService

user_facility_association_router = APIRouter(
    prefix="/user-facility-associations",
    tags=["User Facility Association"],
    dependencies=[Depends(validate_api_key)],
)


@user_facility_association_router.put(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    description="Path operation for updating a user facility association.",
)
def update_user_facility_association(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to update their profile.")],
    user_facility_association_data: UpdateUserFacilityAssociationSchema,
    user_facility_association_service: Annotated[
        UserFacilityAssociationService, Depends(create_user_facility_association_service)
    ],
) -> ResponseSchema:
    """Method for handling facility representative self-registration request."""
    user_facility_association = user_facility_association_service.update(
        user_id=user_id, data_to_update=user_facility_association_data
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=UserFacilityAssociation),  # type: ignore
        data=ReadUserFacilityAssociationSchema(**user_facility_association.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_facility_association_router.get(
    path="/self",
    status_code=status.HTTP_200_OK,
    description="Get a user facility association for current logged in user..",
)
def self_get_user_facility_association(
    request: Request,
    current_active_user: Annotated[User, Depends(get_current_user)],
    user_facility_association_service: Annotated[
        UserFacilityAssociationService, Depends(create_user_facility_association_service)
    ],
) -> ResponseSchema:
    """Method for handling get a user_facility_association by id request.

    Args:
        request (Request): The request object.
        current_active_user (User): The current logged in user.
        user_facility_association_service (UserProfileService): The user_facility_association service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user_facility_association = user_facility_association_service.get_by_id(entity_id=str(current_active_user.id))

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=UserFacilityAssociation),  # type: ignore
        data=ReadUserFacilityAssociationSchema(**user_facility_association.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_facility_association_router.get(
    path="/{user_id}", status_code=status.HTTP_200_OK, description="Get a user facility association by the user id."
)
def get_user_facility_association_by_user_id(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to get their profile.")],
    user_facility_association_service: Annotated[
        UserFacilityAssociationService, Depends(create_user_facility_association_service)
    ],
) -> ResponseSchema:
    """Method for handling get a user_facility_association by id request.

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to get their profile.
        user_facility_association_service (UserProfileService): The user_facility_association service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user_facility_association = user_facility_association_service.get_by_id(entity_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=UserFacilityAssociation),  # type: ignore
        data=ReadUserFacilityAssociationSchema(**user_facility_association.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
