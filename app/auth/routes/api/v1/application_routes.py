from typing import Annotated, Optional

from fastapi import APIRouter, Body, Depends, Path, Query, Request, status

from app.auth.dependencies.api_keys_dependency import create_api_key_service
from app.auth.dependencies.application_dependency import create_application_service
from app.auth.dependencies.auth_dependency import get_current_user, validate_api_key
from app.auth.dependencies.authorization import application_permissions_required, user_permissions_required
from app.auth.models import Application
from app.auth.schemas.request.applications_api_key import CreateApplicationRequestSchema, UpdateApplicationSchema
from app.auth.schemas.response.applications_api_key import ReadApplicationSchema
from app.auth.services.applications__api_key_service import APIKeyService, ApplicationService
from app.auth.utils.constants import APIKeyRevocationReasonConstants, PermissionConstants
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.users.models import User

application_router = APIRouter(
    prefix="/applications",
    tags=["Application"],
    dependencies=[Depends(validate_api_key)],
)


@application_router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
    description="Register application.",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.CREATE_APPLICATION.value]))
    ],
)
async def register_application(
    request: Request,
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
    application_data: Annotated[
        CreateApplicationRequestSchema, Body(..., description="Schema for the data when registering an app.")
    ],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseSchema:
    """Method for handling registering an application request.

    Args:
        request (Request): The request object.
        application_service (ApplicationService): The application service to use.
        application_data (CreateUserRequestSchema): The data for registering the application.
        current_user (User): The current user.

    Returns:
        ResponseSchema: The response data.
    """
    new_application, api_key = application_service.create(current_user=current_user, application_data=application_data)
    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(  # type: ignore
            object_type=Application, extra_info="Copy your api key and store it securely. It will only be shown once."
        ),
        data=ReadApplicationSchema(**new_application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@application_router.post(
    path="/{application_id}/rotate-keys",
    status_code=status.HTTP_201_CREATED,
    description="Rotate application keys.",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.ROTATE_APPLICATION_KEYS.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.ROTATE_APPLICATION_KEYS.value])
        ),
    ],
)
async def rotate_application_key(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to rotate key for.")],
    api_key_service: Annotated[APIKeyService, Depends(create_api_key_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseSchema:
    """Method for handling rotating application keys.

    Args:
        request (Request): The request object.

        application_id (str): The application id to rotate key for.
        api_key_service (APIKeyService): The api key service.
        current_user (User): The current user.

    Returns:
        ResponseSchema: The response data.
    """
    new_api_key = api_key_service.rotate_api_key(application_id=application_id, current_user=current_user)
    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.API_KEY_ROTATED_SUCCESSFULLY,  # type: ignore
        data={
            "api_key": new_api_key,
            "message": "Copy your key and store it securely. It will disappear after leaving this page.",
        },  # type: ignore
        request=request,
    )

    return response_data


@application_router.post(
    path="/{application_id}/revoke-keys",
    status_code=status.HTTP_200_OK,
    description="Revoke application keys.",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.REVOKE_APPLICATION_KEYS.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.REVOKE_APPLICATION_KEYS.value])
        ),
    ],
)
async def revoke_application_keys(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to revoke keys.")],
    api_key_service: Annotated[APIKeyService, Depends(create_api_key_service)],
) -> ResponseSchema:
    """Method for handling revoking an application keys.

    Args:
        request (Request): The request object.

        application_id (str): The application id to rotate key for.
        api_key_service (APIKeyService): The api key service.

    Returns:
        ResponseSchema: The response data.
    """
    api_key_service.revoke_api_keys(
        application_id=application_id, reason=APIKeyRevocationReasonConstants.ADMIN_REVOCATION.value
    )
    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.API_KEYS_REVOKED_SUCCESSFULLY.value,
        data={"revoked": True},  # type: ignore
        request=request,
    )

    return response_data


@application_router.get(
    path="",
    status_code=status.HTTP_200_OK,
    description="Get all applications",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.LIST_APPLICATIONS.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.LIST_APPLICATIONS.value])),
    ],
)
def get_all_applications(
    request: Request,
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
    filters: Annotated[Optional[str], Query(description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Method for handling get all applications request.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    applications = application_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": application_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(applications)})

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Application),  # type: ignore
        data=list(map(lambda application: ReadApplicationSchema(**application.to_dict()), applications)),  # type: ignore
        extras=extras,
        request=request,
    )

    return response_data


@application_router.get(
    path="/{application_id}",
    status_code=status.HTTP_200_OK,
    description="Get application by id",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.VIEW_APPLICATION.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.VIEW_APPLICATION.value])),
    ],
)
def get_application_by_id(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to get.")],
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
) -> ResponseSchema:
    """Method for handling get an application by id request.

    Args:
        request (Request): The request object.
        application_id (str): The id of the application to retrieve.
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    application = application_service.get_by_id(entity_id=application_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Application),  # type: ignore
        data=ReadApplicationSchema(**application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@application_router.put(
    path="/{application_id}",
    status_code=status.HTTP_200_OK,
    description="Update an application",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.UPDATE_APPLICATION.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.UPDATE_APPLICATION.value])),
    ],
)
def update_application(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to update.")],
    data_to_update: UpdateApplicationSchema,
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
) -> ResponseSchema:
    """Method for handling update an application by id request.

    Args:
        request (Request): The request object.
        application_id (str): The id of the application to update.
        data_to_update (UpdateApplicationSchema): The data to update application with.
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    application = application_service.update(application_id=application_id, data_to_update=data_to_update)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=Application),  # type: ignore
        data=ReadApplicationSchema(**application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@application_router.put(
    path="/{application_id}/activate",
    status_code=status.HTTP_200_OK,
    description="Activate an application",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.ACTIVATE_APPLICATION.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.ACTIVATE_APPLICATION.value])
        ),
    ],
)
def activate_application(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to activate.")],
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
) -> ResponseSchema:
    """Method for handling activate an application by id request.

    Args:
        request (Request): The request object.
        application_id (str): The id of the application to activate.
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    application, plain_text = application_service.activate_application(application_id=application_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.APPLICATION_ACTIVATED.value,  # type: ignore
        data=ReadApplicationSchema(**application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@application_router.put(
    path="/{application_id}/deactivate",
    status_code=status.HTTP_200_OK,
    description="Deactivate an application",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.DEACTIVATE_APPLICATION.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.DEACTIVATE_APPLICATION.value])
        ),
    ],
)
def deactivate_application(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to deactivate.")],
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
) -> ResponseSchema:
    """Method for handling deactivate an application by id request.

    Args:
        request (Request): The request object.
        application_id (str): The id of the application to deactivate.
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    application = application_service.deactivate_application(application_id=application_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.APPLICATION_DEACTIVATED.value,  # type: ignore
        data=ReadApplicationSchema(**application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@application_router.delete(
    path="/{application_id}",
    status_code=status.HTTP_200_OK,
    description="Delete an application",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.DELETE_APPLICATION.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.DELETE_APPLICATION.value])),
    ],
)
def delete_application(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to delete.")],
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
) -> ResponseSchema:
    """Method for handling delete an application by id request.

    Args:
        request (Request): The request object.
        application_id (str): The id of the application to delete.
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    application = application_service.delete(entity_id=application_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=Application),  # type: ignore
        data=ReadApplicationSchema(**application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@application_router.patch(
    path="/{application_id}/restore",
    status_code=status.HTTP_200_OK,
    description="Restore a deleted application",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.RESTORE_APPLICATION.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.RESTORE_APPLICATION.value])),
    ],
)
def restore_application(
    request: Request,
    application_id: Annotated[str, Path(..., description="The id of the application to restore.")],
    application_service: Annotated[ApplicationService, Depends(create_application_service)],
) -> ResponseSchema:
    """Method for handling restore an application by id request.

    Args:
        request (Request): The request object.
        application_id (str): The id of the application to restore.
        application_service (ApplicationService): The application service to use.

    Returns:
        ResponseSchema: The response data.
    """
    application = application_service.restore(entity_id=application_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=Application),  # type: ignore
        data=ReadApplicationSchema(**application.to_dict()),  # type: ignore
        request=request,
    )

    return response_data
