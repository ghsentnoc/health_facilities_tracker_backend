from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.auth.dependencies.role_service_dependency import create_role_service
from app.auth.docs.roles_docs import (
    create_role_docs,
    delete_role_docs,
    get_all_roles_docs,
    get_role_by_id_docs,
    restore_role_docs,
    update_role_docs,
)
from app.auth.models import Role
from app.auth.schemas.request.role import CreateRoleSchema, UpdateRoleSchema
from app.auth.schemas.response.role import ReadRoleSchema
from app.auth.services.role_service import RoleService
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages

role_router = APIRouter(prefix="/roles", tags=["Role"], dependencies=[Depends(validate_api_key)])


@role_router.post(path="", status_code=status.HTTP_201_CREATED, description=create_role_docs)
def create_role(
    request: Request, role_data: CreateRoleSchema, role_service: Annotated[RoleService, Depends(create_role_service)]
) -> ResponseSchema:
    """Method for handling creating a new role.

    Args:
        request (Request): The request object.
        role_data (CreateRoleSchema): The data needed to create the role.
        role_service (RoleService): The role service to use.

    Returns:
        ResponseSchema: The response data.
    """
    role = role_service.create(role_data=role_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Role),  # type: ignore
        data=ReadRoleSchema(**role.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@role_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_roles_docs)
def get_all_roles(
    request: Request,
    role_service: Annotated[RoleService, Depends(create_role_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all roles request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        role_service (RoleService): The role service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    roles = role_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": role_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(roles)})

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Role),  # type: ignore
        data=list(map(lambda role: ReadRoleSchema(**role.to_dict()), roles)),  # type: ignore
        extras=extras,
        request=request,
    )

    return response_data


@role_router.get(path="/{role_id}", status_code=status.HTTP_200_OK, description=get_role_by_id_docs)
def get_role_by_id(
    request: Request,
    role_id: Annotated[str, Path(..., description="The id of the role to get.")],
    role_service: Annotated[RoleService, Depends(create_role_service)],
) -> ResponseSchema:
    """Method for handling get a role by id request.

    Args:
        request (Request): The request object.
        role_id (str): The id of the role to retrieve.
        role_service (RoleService): The role service to use.

    Returns:
        ResponseSchema: The response data.
    """
    role = role_service.get_by_id(entity_id=role_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Role),  # type: ignore
        data=ReadRoleSchema(**role.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@role_router.put(path="/{role_id}", status_code=status.HTTP_200_OK, description=update_role_docs)
def update_role(
    request: Request,
    role_id: Annotated[str, Path(..., description="The id of the role to get.")],
    data_to_update: UpdateRoleSchema,
    role_service: Annotated[RoleService, Depends(create_role_service)],
) -> ResponseSchema:
    """Method for handling update a role by id request.

    Args:
        request (Request): The request object.
        role_id (str): The id of the role to update.
        data_to_update (UpdateRoleSchema): The data to update role with.
        role_service (RoleService): The role service to use.

    Returns:
        ResponseSchema: The response data.
    """
    role = role_service.update(role_id=role_id, data_to_update=data_to_update)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=Role),  # type: ignore
        data=ReadRoleSchema(**role.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@role_router.delete(path="/{role_id}", status_code=status.HTTP_200_OK, description=delete_role_docs)
def delete_role(
    request: Request,
    role_id: Annotated[str, Path(..., description="The id of the role to get.")],
    role_service: Annotated[RoleService, Depends(create_role_service)],
) -> ResponseSchema:
    """Method for handling delete a role by id request.

    Args:
        request (Request): The request object.
        role_id (str): The id of the role to delete.
        role_service (RoleService): The role service to use.

    Returns:
        ResponseSchema: The response data.
    """
    role = role_service.delete(entity_id=role_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=Role),  # type: ignore
        data=ReadRoleSchema(**role.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@role_router.patch(path="/{role_id}/restore", status_code=status.HTTP_200_OK, description=restore_role_docs)
def restore_role(
    request: Request,
    role_id: Annotated[str, Path(..., description="The id of the role to get.")],
    role_service: Annotated[RoleService, Depends(create_role_service)],
) -> ResponseSchema:
    """Method for handling restore a role by id request.

    Args:
        request (Request): The request object.
        role_id (str): The id of the role to restore.
        role_service (RoleService): The role service to use.

    Returns:
        ResponseSchema: The response data.
    """
    role = role_service.restore(entity_id=role_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=Role),  # type: ignore
        data=ReadRoleSchema(**role.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
