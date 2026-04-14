from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.users.dependencies.user_service_dependency import create_user_service
from app.users.docs.users_docs import (
    delete_user_docs,
    get_all_users_docs,
    get_user_by_id_docs,
    register_admin_docs,
    register_facility_representative_docs,
    restore_user_docs,
)
from app.users.models import User
from app.users.schemas.request.user import (
    CreateFacilityRepSchema,
    CreateUserByAdminSchema,
)
from app.users.schemas.response.user import ReadUserSchema
from app.users.services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["User"], dependencies=[Depends(validate_api_key)])


@user_router.post(path="/register/by-admin", status_code=status.HTTP_201_CREATED, description=register_admin_docs)
async def register_admin(
    request: Request,
    user_data: CreateUserByAdminSchema,
    user_service: Annotated[UserService, Depends(create_user_service)],
) -> ResponseSchema:
    """Method for handling admin registration request."""
    user = await user_service.register_user_by_admin(user_data=user_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_router.post(
    path="/register/facility-representative",
    status_code=status.HTTP_201_CREATED,
    description=register_facility_representative_docs,
)
async def register_facility_representative(
    request: Request,
    user_data: CreateFacilityRepSchema,
    user_service: Annotated[UserService, Depends(create_user_service)],
) -> ResponseSchema:
    """Method for handling facility representative self-registration request."""
    user = await user_service.register_as_facility_representative(user_data=user_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_users_docs)
def get_all_users(
    request: Request,
    user_service: Annotated[UserService, Depends(create_user_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all users request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        user_service (UserService): The user service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    users = user_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": user_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(users)})

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=User),  # type: ignore
        data=list(map(lambda user: ReadUserSchema(**user.to_dict()), users)),  # type: ignore
        extras=extras,
        request=request,
    )

    return response_data


@user_router.get(path="/{user_id}", status_code=status.HTTP_200_OK, description=get_user_by_id_docs)
def get_user_by_id(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to get.")],
    user_service: Annotated[UserService, Depends(create_user_service)],
) -> ResponseSchema:
    """Method for handling get a user by id request.

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to retrieve.
        user_service (UserService): The user service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user = user_service.get_by_id(entity_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_router.patch(path="/{user_id}/approve", status_code=status.HTTP_200_OK, description="Approve a user")
def approve_user(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to approve.")],
    user_service: Annotated[UserService, Depends(create_user_service)],
) -> ResponseSchema:
    """Method for handling approve a user by id request.

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to approve.
        user_service (UserService): The user service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user = user_service.approve_facility_representative(user_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_router.delete(path="/{user_id}", status_code=status.HTTP_200_OK, description=delete_user_docs)
def delete_user(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to delete.")],
    user_service: Annotated[UserService, Depends(create_user_service)],
) -> ResponseSchema:
    """Method for handling delete a user by id request.

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to delete.
        user_service (UserService): The user service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user = user_service.delete(entity_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@user_router.patch(path="/{user_id}/restore", status_code=status.HTTP_200_OK, description=restore_user_docs)
def restore_user(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to restore.")],
    user_service: Annotated[UserService, Depends(create_user_service)],
) -> ResponseSchema:
    """Method for handling restore a user by id request.

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to restore.
        user_service (UserService): The user service to use.

    Returns:
        ResponseSchema: The response data.
    """
    user = user_service.restore(entity_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
