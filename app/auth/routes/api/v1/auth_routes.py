from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request, status

from app.auth.dependencies.auth_service_dependency import create_auth_service
from app.auth.docs.auth_docs import (
    register_user_docs,
    request_password_reset_docs,
    resend_account_verification_link_docs,
    reset_password_docs,
    verify_account_docs,
    verify_password_reset_token_docs,
)
from app.auth.schemas.request.auth import EmailSchema, PasswordResetSchema, TokenDataSchema
from app.auth.services.auth_service import AuthService
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.users.models import User
from app.users.schemas.request.user import CreateUserRequestSchema
from app.users.schemas.response.user import ReadUserSchema

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(path="/register", status_code=status.HTTP_201_CREATED, description=register_user_docs)
async def register_user(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    user_data: Annotated[
        CreateUserRequestSchema, Body(..., description="Schema for the data when registering a user.")
    ],
) -> ResponseSchema:
    """Method for handling registering a user request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        user_data (CreateUserRequestSchema): The data for registering the user.

    Returns:
        ResponseSchema: The response data.
    """
    new_user = await auth_service.register_user(user_data=user_data)
    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(  # type: ignore
            object_type=User, extra_info="Check your email to verify your account."
        ),
        data=ReadUserSchema(**new_user.to_dict()),  # type: ignore
        request=request,
    )

    return response_data


@auth_router.post(path="/verify-account", status_code=status.HTTP_200_OK, description=verify_account_docs)
def verify_account(
    request: Request,
    auth_service: Annotated[AuthService, Depends(create_auth_service)],
    verify_token_data: Annotated[TokenDataSchema, Body(..., description="Schema for the token data.")],
) -> ResponseSchema:
    """Method for handling verifying account request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        verify_token_data (TokenDataSchema): The token data for verifying the account.

    Returns:
        ResponseSchema: The response data.
    """
    verified_user_response = auth_service.verify_account(token_data=verify_token_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
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
) -> ResponseSchema:
    """Method for handling resending account verification link request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        resend_account_verification_request_data (EmailSchema): The data needed to resend the account verification link.

    Returns:
        ResponseSchema: The response data.
    """
    verified_user_response = await auth_service.resend_account_verification_email(
        resend_account_verification_email_data=resend_account_verification_request_data
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
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
) -> ResponseSchema:
    """Method for handling resending account verification link request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        request_password_reset_data (EmailSchema): The data needed to resend the account verification link.

    Returns:
        ResponseSchema: The response data.
    """
    request_password_reset_response = await auth_service.request_password_reset(email_data=request_password_reset_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
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
        status_code=status.HTTP_201_CREATED,
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
) -> ResponseSchema:
    """Method for handling reset password request.

    Args:
        request (Request): The request object.
        auth_service (AuthService): The auth service to use.
        password_reset_data (PasswordResetSchema): The password reset data.

    Returns:
        ResponseSchema: The response data.
    """
    reset_password_response = auth_service.reset_password(password_reset_data=password_reset_data)

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.PASSWORD_RESET.value,  # type: ignore
        data=reset_password_response,  # type: ignore
        request=request,
    )

    return response_data
