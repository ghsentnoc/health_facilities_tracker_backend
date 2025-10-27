from pydantic import BaseModel, EmailStr, field_validator

from app.core.custom_exceptions import InvalidEmailError
from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_email, is_valid_password


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


class VerifyResetPasswordTokenSchema(EmailSchema):
    """Schema for when verifying a reset password token."""

    token: str


class AccountVerificationResponseSchema(EmailSchema):
    """Schema for the response when an account has been verified."""

    message: str
    is_verified: bool


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


class AlreadyVerifiedErrorDataSchema(EmailSchema):
    """Schema for when a user is already verified."""

    is_verified: bool
