from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.core.custom_exceptions import InvalidEmailError
from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_email, is_valid_password, is_valid_uuid
from app.users.schemas.request.user_profile import BaseUserProfileSchema


class UserFacilitySchema(BaseModel):
    """Schema for user facility information when registering as a facility representative."""

    facility_id: str

    @field_validator("facility_id")
    @classmethod
    def validate_facility_id(cls, value: str) -> str:
        """Check if the facility id is valid.

        Args:
            value (str): The facility id to validate.

        Returns:
            str: The validated id.
        """
        if not is_valid_uuid(uuid_to_test=value):
            raise ValueError(ErrorMessages.INVALID_ID.value)
        return value


class BaseUserSchema(BaseModel):
    """The base schema for user-related operations."""

    email: str
    user_profile: BaseUserProfileSchema

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


class CreateUserByAdminSchema(BaseUserSchema):
    """The schema for creating a user by an admin."""

    role_ids: list[str]
    facility_info: Optional[UserFacilitySchema] = None

    @field_validator("role_ids")
    @classmethod
    def validate_facility_id(cls, value: list[str]) -> list[str]:
        """Check if the facility id is valid.

        Args:
            value (list[str]): The list of role ids to validate.

        Returns:
            list[str]: The validated list of role ids.
        """
        for role_id in value:
            if not is_valid_uuid(uuid_to_test=role_id):
                raise ValueError(ErrorMessages.INVALID_ID.value)
        return value


class CreateFacilityRepSchema(BaseUserSchema):
    """The schema for creating a facility representative user."""

    password: str
    facility_info: UserFacilitySchema

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Check if the password is a valid password.

        Args:
            value (str): The password to validate

        Returns:
            str: The validate password.
        """
        if not is_valid_password(password=value):
            raise ValueError(ErrorMessages.INVALID_PASSWORD.value)
        return value


class CreateUserSchema(BaseModel):
    """The schema for creating a general user."""

    email: str
    password_hash: Optional[str] = None

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
