from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request, status

from app.auth.dependencies.auth_dependency import get_current_user, validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.users.dependencies.user_profile_service_dependency import create_user_profile_service
from app.users.models import User, UserProfile
from app.users.schemas.request.user_profile import UpdateUserProfileSchema
from app.users.schemas.response.user_profile import ReadUserProfileSchema
from app.users.services import UserProfileService

user_profile_router = APIRouter(
    prefix="/user-profiles",
    tags=["User Profile"],
    dependencies=[Depends(validate_api_key)],
)


@user_profile_router.put(
    path="/self", status_code=status.HTTP_200_OK, description="Path operation for self updating a user profile."
)
def self_update_user_profile(
    request: Request,
    current_active_user: Annotated[User, Depends(get_current_user)],
    user_profile_data: UpdateUserProfileSchema,
    user_profile_service: Annotated[UserProfileService, Depends(create_user_profile_service)],
) -> ResponseSchema:
    """Method for handling facility representative self-registration request."""
    user_profile = user_profile_service.update(user_id=str(current_active_user.id), data_to_update=user_profile_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=UserProfile),  # type: ignore
        data=ReadUserProfileSchema(**user_profile.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_profile_router.put(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    description="Path operation for updating a user profile.",
)
def update_user_profile(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to update their profile.")],
    user_profile_data: UpdateUserProfileSchema,
    user_profile_service: Annotated[UserProfileService, Depends(create_user_profile_service)],
) -> ResponseSchema:
    """Method for handling facility representative self-registration request."""
    user_profile = user_profile_service.update(user_id=user_id, data_to_update=user_profile_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=UserProfile),  # type: ignore
        data=ReadUserProfileSchema(**user_profile.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_profile_router.get(
    path="/self", status_code=status.HTTP_200_OK, description="Get a user profile for current logged in user.."
)
def self_get_user_profile(
    request: Request,
    current_active_user: Annotated[User, Depends(get_current_user)],
    user_profile_service: Annotated[UserProfileService, Depends(create_user_profile_service)],
) -> ResponseSchema:
    """Method for handling get a user_profile by id request.

    Args:
        request (Request): The request object.
        current_active_user (User): The current logged in user.
        user_profile_service (UserProfileService): The user_profile service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user_profile = user_profile_service.get_by_id(entity_id=str(current_active_user.id))

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=UserProfile),  # type: ignore
        data=ReadUserProfileSchema(**user_profile.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_profile_router.get(
    path="/{user_id}", status_code=status.HTTP_200_OK, description="Get a user profile by the user id."
)
def get_user_profile_by_user_id(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to get their profile.")],
    user_profile_service: Annotated[UserProfileService, Depends(create_user_profile_service)],
) -> ResponseSchema:
    """Method for handling get a user_profile by id request.

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to get their profile.
        user_profile_service (UserProfileService): The user_profile service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user_profile = user_profile_service.get_by_id(entity_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=UserProfile),  # type: ignore
        data=ReadUserProfileSchema(**user_profile.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
