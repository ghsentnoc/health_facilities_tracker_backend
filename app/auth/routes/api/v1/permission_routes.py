from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.auth.dependencies.permission_service_dependency import create_permission_service
from app.auth.docs.permission_docs import get_all_permissions_docs
from app.auth.models import Permission
from app.auth.schemas.response.permission import ReadPermissionSchema
from app.auth.services.permission_service import PermissionService
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages

permission_router = APIRouter(
    prefix="/permissions",
    tags=["Permission"],
    dependencies=[Depends(validate_api_key)],
)


@permission_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_permissions_docs)
def get_all_permissions(
    request: Request,
    permission_service: Annotated[PermissionService, Depends(create_permission_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all permissions request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        permission_service (PermissionService): The permission service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    permissions = permission_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": permission_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(permissions)})

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Permission),  # type: ignore
        data=list(map(lambda permission: ReadPermissionSchema(**permission.to_dict()), permissions)),  # type: ignore
        extras=extras,
        request=request,
    )

    return response_data
