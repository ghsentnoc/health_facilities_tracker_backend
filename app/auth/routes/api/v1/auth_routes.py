from typing import Annotated, Literal

from fastapi import APIRouter, Body, Depends, Header, Path, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies.auth_dependency import get_current_user, validate_api_key
from app.auth.dependencies.auth_service_dependency import create_auth_service
from app.auth.dependencies.authorization import application_permissions_required, user_permissions_required
from app.auth.docs.auth_docs import (
    request_password_reset_docs,
    resend_account_verification_link_docs,
    reset_password_docs,
    verify_account_docs,
    verify_password_reset_token_docs,
)
from app.auth.models import Application
from app.auth.schemas.request.auth import (
    ChangePasswordSchema,
    EmailSchema,
    PasswordResetSchema,
    SwitchRoleSchema,
    TokenDataSchema,
    UpdateUserRoleSchema,
)
from app.auth.services.auth_service import AuthService
from app.auth.utils.constants import PermissionConstants
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.users.models.users import User
from app.users.schemas.response.user import ReadUserSchema

auth_router = APIRouter(prefix="/auth", tags=["Auth"], dependencies=[Depends(validate_api_key)])


@auth_router.post(path="/verify-account", status_code=status.HTTP_200_OK, description=verify_account_docs)
def verify_account(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    verify_token_data: Annotated[TokenDataSchema, Body(..., description="Schema for the token data.")],
    application: Annotated[Application, Depends(validate_api_key)],
) -> ResponseSchema:
    """Method for handling verifying account request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        verify_token_data (TokenDataSchema): The token data for verifying the account.
        application (Application): The application making the request.

    Returns:
        ResponseSchema: The response data.
    """
    verified_user_response = auth_service.verify_account(token_data=verify_token_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=verified_user_response.message,  # type: ignore
        data=verified_user_response.model_dump(),  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/resend-account-verification-link",
    status_code=status.HTTP_200_OK,
    description=resend_account_verification_link_docs,
)
async def resend_account_verification_link(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    resend_account_verification_request_data: Annotated[
        EmailSchema, Body(..., description="Schema for resend account verification.")
    ],
    application: Annotated[Application, Depends(validate_api_key)],
) -> ResponseSchema:
    """Method for handling resending account verification link request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        resend_account_verification_request_data (EmailSchema): The data needed to resend the account verification link.
        application (Application): The application making the request.

    Returns:
        ResponseSchema: The response data.
    """
    verified_user_response = await auth_service.resend_account_verification_email(
        resend_account_verification_email_data=resend_account_verification_request_data, application=application
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=verified_user_response,  # type: ignore
        data={},  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/request-password-reset",
    status_code=status.HTTP_200_OK,
    description=request_password_reset_docs,
)
async def request_password_reset(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    request_password_reset_data: Annotated[EmailSchema, Body(..., description="Schema for password reset request.")],
    application: Annotated[Application, Depends(validate_api_key)],
) -> ResponseSchema:
    """Method for handling resending account verification link request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        request_password_reset_data (EmailSchema): The data needed to resend the account verification link.
        application (Application): The application making the request.

    Returns:
        ResponseSchema: The response data.
    """
    request_password_reset_response = await auth_service.request_password_reset(
        email_data=request_password_reset_data, application=application
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=request_password_reset_response,  # type: ignore
        data={},  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/verify-password-reset-token",
    status_code=status.HTTP_200_OK,
    description=verify_password_reset_token_docs,
)
def verify_password_reset_token(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    password_reset_token: Annotated[TokenDataSchema, Body(..., description="Schema for password reset token.")],
) -> ResponseSchema:
    """Method for handling verifying password reset token request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        password_reset_token (TokenDataSchema): The token data to verify.

    Returns:
        ResponseSchema: The response data.
    """
    verify_password_reset_token_response = auth_service.verify_password_reset_token(token_data=password_reset_token)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.PASSWORD_RESET_TOKEN_VERIFIED.value,  # type: ignore
        data=verify_password_reset_token_response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/reset-password",
    status_code=status.HTTP_200_OK,
    description=reset_password_docs,
)
def reset_password(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    password_reset_data: Annotated[PasswordResetSchema, Body(..., description="Schema for password reset.")],
    application: Annotated[Application, Depends(validate_api_key)],
) -> ResponseSchema:
    """Method for handling reset password request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        password_reset_data (PasswordResetSchema): The password reset data.
        application (Application): The application making the request.

    Returns:
        ResponseSchema: The response data.
    """
    _ = auth_service.reset_password(password_reset_data=password_reset_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.PASSWORD_RESET.value,  # type: ignore
        data={},  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/authenticate",
    status_code=status.HTTP_200_OK,
    description="Authenticate an email_password user.",
)
def authenticate_user(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)],
    application: Annotated[Application, Depends(validate_api_key)],
    device_id: Annotated[str, Header(..., description="The device ID making the request.")],
    client_type: Annotated[
        Literal["web", "mobile", "desktop", "api", "cli"],
        Header(..., description="The client type making the request."),
    ],
) -> ResponseSchema:
    """Method for handling authentication.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        user_credentials (AuthenticationForm): The user credentials needed for authentication
        application (Application): The application making the request.
        device_id (str): The device ID making the request.
        client_type (Literal): The client type making the request.

    Returns:
        ResponseSchema: The response data.
    """
    authentication_response = auth_service.authenticate_user(
        user_credentials=user_credentials, application=application, device_id=device_id, client_type=client_type
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.AUTHENTICATED.value,  # type: ignore
        data=authentication_response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/refresh-token",
    status_code=status.HTTP_200_OK,
    description="Refresh a user's access token",
)
async def refresh_token(
    request: Request,
    token: Annotated[TokenDataSchema, Body(..., description="The refresh token")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    device_id: Annotated[str, Header(..., description="The device ID making the request.")],
    client_type: Annotated[
        Literal["web", "mobile", "desktop", "api", "cli"],
        Header(..., description="The client type making the request."),
    ],
    application: Annotated[Application, Depends(validate_api_key)],
) -> ResponseSchema:
    """Refresh a user's access token

    Args:
        request (Request): The request object.
        token (RefreshTokenSchema): The refresh token.
        auth_service (AuthService): The auth service to use.
        device_id (str): The device ID making the request.
        client_type (Literal): The client type making the request.
        application (Application): The application making the request.

    Returns:
        ResponseSchema: The response data
    """
    refresh_token_response = auth_service.refresh_token(token=token, device_id=device_id, client_type=client_type)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.AUTHENTICATED.value,  # type: ignore
        data=refresh_token_response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/change-password",
    status_code=status.HTTP_200_OK,
    description="Change a user's password",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.CHANGE_USER_PASSWORD.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.CHANGE_USER_PASSWORD.value])
        ),
    ],
)
async def change_password(
    request: Request,
    change_password_data: Annotated[ChangePasswordSchema, Body(..., description="The change password data")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseSchema:
    """Change a user's password

    Args:
        request (Request): The request object.
        change_password_data (ChangePasswordSchema): The data to change a password
        auth_service (AuthService): The auth service to use.
        current_user (User): The current user.

    Returns:
        ResponseSchema: The response data
    """
    change_password_response = auth_service.change_password(
        current_active_user=current_user, change_password_data=change_password_data
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.PASSWORD_CHANGED_SUCCESSFULLY.value,  # type: ignore
        data=ReadUserSchema(**change_password_response.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/{user_id}/revoke-tokens",
    status_code=status.HTTP_200_OK,
    description="Revoke a user's tokens",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.REVOKE_USER_TOKENS.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.REVOKE_USER_TOKENS.value])),
    ],
)
async def revoke_user_tokens(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to revoke their tokens")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
) -> ResponseSchema:
    """Revoke a user's tokens

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to revoke their tokens.
        auth_service (AuthService): The auth service to use.

    Returns:
        ResponseSchema: The response data
    """
    response = auth_service.revoke_user_tokens(user_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.TOKENS_REVOKED_SUCCESSFULLY.value,  # type: ignore
        data=response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/{user_id}/suspend-account",
    status_code=status.HTTP_200_OK,
    description="Suspend a user's account",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.SUSPEND_USER_ACCOUNT.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.SUSPEND_USER_ACCOUNT.value])
        ),
    ],
)
async def suspend_user_account(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to suspend their account")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
) -> ResponseSchema:
    """Suspend a user's account

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to suspend their account.
        auth_service (AuthService): The auth service to use.

    Returns:
        ResponseSchema: The response data
    """
    response = auth_service.suspend_user_account(user_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.ACCOUNT_SUSPENDED_SUCCESSFULLY.value,  # type: ignore
        data=response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/{user_id}/reactivate-account",
    status_code=status.HTTP_200_OK,
    description="Reactivate a user's account",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.REACTIVATE_USER_ACCOUNT.value])),
        Depends(
            application_permissions_required(required_permissions=[PermissionConstants.REACTIVATE_USER_ACCOUNT.value])
        ),
    ],
)
async def reactivate_user_account(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to reactivate their account")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
) -> ResponseSchema:
    """Reactivate a user's account

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to reactivate their account.
        auth_service (AuthService): The auth service to use.

    Returns:
        ResponseSchema: The response data
    """
    response = auth_service.reactivate_user_account(user_id=user_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.ACCOUNT_REACTIVATED_SUCCESSFULLY.value,  # type: ignore
        data=response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/{user_id}/update-roles",
    status_code=status.HTTP_200_OK,
    description="Update a user's roles",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.UPDATE_USER_ROLES.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.UPDATE_USER_ROLES.value])),
    ],
)
async def update_user_roles(
    request: Request,
    user_id: Annotated[str, Path(..., description="The id of the user to update their roles")],
    role_data: Annotated[UpdateUserRoleSchema, Body(..., description="The role data to update user with.")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
) -> ResponseSchema:
    """Update a user's roles

    Args:
        request (Request): The request object.
        user_id (str): The id of the user to update their roles.
        role_data (UpdateUserRoleSchema): The role data to update the user with.
        auth_service (AuthService): The auth service to use.

    Returns:
        ResponseSchema: The response data
    """
    response = auth_service.update_user_role(user_id=user_id, role_data=role_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=User),  # type: ignore
        data=ReadUserSchema(**response.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/switch-role",
    status_code=status.HTTP_200_OK,
    description="Switch a user's active role",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.SWITCH_USER_ROLE.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.SWITCH_USER_ROLE.value])),
    ],
)
async def switch_user_role(
    request: Request,
    switch_role_data: Annotated[SwitchRoleSchema, Body(..., description="The role data to switch user to.")],
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    application: Annotated[Application, Depends(validate_api_key)],
    device_id: Annotated[str, Header(..., description="The device ID making the request.")],
) -> ResponseSchema:
    """Switch a user's active role

    Args:
        request (Request): The request object.
        switch_role_data (SwitchRoleSchema): The role data to switch the user to.
        auth_service (AuthService): The auth service to use.
        current_user (User): The current user.
        application (Application): The application making the request.
        device_id (str): The device ID making the request.

    Returns:
        ResponseSchema: The response data
    """
    response = auth_service.switch_user_role(
        current_user=current_user, data=switch_role_data, application=application, device_id=device_id
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.ROLE_SWITCHED_SUCCESSFULLY.value,  # type: ignore
        data=response,  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    description="Logout a user",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.LOGOUT_USER.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.LOGOUT_USER.value])),
    ],
)
async def logout(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    current_user: Annotated[User, Depends(get_current_user)],
    device_id: Annotated[str, Header(..., description="The device ID making the request.")],
) -> ResponseSchema:
    """Logout a user from the system.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        current_user (User): The current user.
        device_id (str): The device ID making the request.

    Returns:
        ResponseSchema: The response data
    """
    _ = auth_service.logout(current_user=current_user, device_id=device_id)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.LOGOUT.value,  # type: ignore
        data={},  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_200_OK,
    description="Logout a user",
    dependencies=[
        Depends(user_permissions_required(required_permissions=[PermissionConstants.LOGOUT_USER.value])),
        Depends(application_permissions_required(required_permissions=[PermissionConstants.LOGOUT_USER.value])),
    ],
)
async def logout_all_sessions(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResponseSchema:
    """Logout a user from the system.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        current_user (User): The current user.

    Returns:
        ResponseSchema: The response data
    """
    _ = auth_service.logout_all_sessions(current_user=current_user)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.LOGOUT.value,  # type: ignore
        data={},  # type: ignore
        request=request,
    )

    return response_data
