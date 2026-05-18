from typing import Annotated, Literal, Optional, Union

from fastapi.param_functions import Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, field_validator
from typing_extensions import Doc

from app.core.custom_exceptions import InvalidEmailError
from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_email, is_valid_password, is_valid_uuid
from app.users.schemas.response.user import ReadUserRoleSchema


class AuthenticationForm(OAuth2PasswordRequestForm):
    """Custom authentication form to include phone number."""

    def __init__(
        self,
        *,
        grant_type: Annotated[
            Union[str, None],
            Form(pattern="^password$"),
            Doc(
                """
                    The OAuth2 spec says it is required and MUST be the fixed string
                    "password". Nevertheless, this dependency class is permissive and
                    allows not passing it. If you want to enforce it, use instead the
                    `OAuth2PasswordRequestFormStrict` dependency.
                    """
            ),
        ] = None,
        username: Annotated[
            str,
            Form(),
            Doc(
                """
                    `username` string. The OAuth2 spec requires the exact field name
                    `username`.
                    """
            ),
        ],
        user_identifier: Annotated[
            Literal["email", "phone_number"],
            Form(),
            Doc(
                """
                    The user identifier, which can be either an email or a phone number.
                    This field is not part of the OAuth2 spec, but is required for our
                    custom authentication flow.
                    """
            ),
        ],
        password: Annotated[
            str,
            Form(json_schema_extra={"format": "password"}),
            Doc(
                """
                    `password` string. The OAuth2 spec requires the exact field name
                    `password`.
                    """
            ),
        ],
        scope: Annotated[
            str,
            Form(),
            Doc(
                """
                    A single string with actually several scopes separated by spaces. Each
                    scope is also a string.

                    For example, a single string with:

                    ```python
                    "items:read items:write users:read profile openid"
                    ````

                    would represent the scopes:

                    * `items:read`
                    * `items:write`
                    * `users:read`
                    * `profile`
                    * `openid`
                    """
            ),
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form(),
            Doc(
                """
                    If there's a `client_id`, it can be sent as part of the form fields.
                    But the OAuth2 specification recommends sending the `client_id` and
                    `client_secret` (if any) using HTTP Basic auth.
                    """
            ),
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form(json_schema_extra={"format": "password"}),
            Doc(
                """
                    If there's a `client_password` (and a `client_id`), they can be sent
                    as part of the form fields. But the OAuth2 specification recommends
                    sending the `client_id` and `client_secret` (if any) using HTTP Basic
                    auth.
                    """
            ),
        ] = None,
    ) -> None:
        """Initialize the authentication form."""
        self.user_identifier = user_identifier

        super().__init__(
            username=username,
            password=password,
            scope=scope,
            grant_type=grant_type,
            client_id=client_id,
            client_secret=client_secret,
        )


class TokenDataSchema(BaseModel):
    """Schema for account verification token."""

    token: str


class EmailSchema(BaseModel):
    """Schema for user email."""

    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: EmailStr) -> EmailStr:
        """Check if the email is a valid email.

        Args:
            value (EmailStr): The email to validate.

        Returns:
            EmailStr: The validated email.
        """
        if not is_valid_email(email=str(value)):
            raise InvalidEmailError(ErrorMessages.INVALID_EMAIL.value)
        return value


class AuthenticationTokenSchema(BaseModel):
    """Schema for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    extra_info: Optional[str | dict | list | int] = None


class VerifyResetPasswordTokenSchema(EmailSchema):
    """Schema for when verifying a reset password token."""

    token: str


class AccountVerificationResponseSchema(EmailSchema):
    """Schema for the response when an account has been verified."""

    message: str
    is_verified: bool
    roles: list[ReadUserRoleSchema]


class PasswordResetSchema(EmailSchema):
    """Schema for when resetting a password."""

    password: str
    token: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate the password field and return it as a string

        Args:
            password (str): The password to validate

        Returns:
            str: The validated password

        Raises:
                ValueError: If the password is not valid
        """
        if not is_valid_password(password=password):
            raise ValueError(ErrorMessages.INVALID_PASSWORD.value)
        return password


# class RefreshTokenSchema(BaseModel):
#     refresh_token: str


class AlreadyVerifiedOrPasswordSetDataSchema(EmailSchema):
    """Schema for when a user is already verified."""

    is_verified: bool
    # password_set: bool


class CreatePasswordSchema(BaseModel):
    """Schema for when a user is creating their password."""

    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Check if the user password is valid.

        Args:
            value (str): The password to validate.

        Returns:
            str: The validated password.
        """
        if not is_valid_password(password=value):
            raise ValueError(ErrorMessages.INVALID_PASSWORD.value)
        return value


class ChangePasswordSchema(BaseModel):
    """Schema for when changing a password."""

    current_password: str
    new_password: str

    @field_validator("current_password", "new_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Check if the user password is valid.

        Args:
            value (str): The password to validate.

        Returns:
            str: The validated password.
        """
        if not is_valid_password(password=value):
            raise ValueError(ErrorMessages.INVALID_PASSWORD.value)
        return value


class AccountSuspendedResponseSchema(BaseModel):
    """Schema for when a user account has been suspended."""

    email: str
    is_suspended: bool


class TokensRevokedResponseSchema(BaseModel):
    """Schema for when a user's tokens have been revoked."""

    email: str
    revoked: bool


class LoggedOutResponseSchema(BaseModel):
    """Schema for when a user is logged out."""

    is_logout: bool


class UpdateUserRoleSchema(BaseModel):
    """Schema for updating a user's role."""

    role_ids: list[str]


class SwitchRoleSchema(BaseModel):
    """Schema for switching a user's role."""

    role_id: str

    @field_validator("role_id")
    @classmethod
    def validate_role_id(cls, value: str) -> str:
        """Check if the role id is valid.

        Args:
            value (str): The role id to validate.

        Returns:
            str: The validated role id.
        """
        if not is_valid_uuid(uuid_to_test=value):
            raise ValueError(ErrorMessages.INVALID_ID.value)
        return value
