from typing import Optional

from pydantic import BaseModel, field_validator

from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_telephone_number, is_valid_uuid


class BaseUserProfileSchema(BaseModel):
    """Base schema for user profile request and response."""

    first_name: str
    last_name: str
    phone_number: str
    country: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """Check if the phone number is valid.

        Args:
            value (str): The phone number to validate

        Returns:
            str: The validated phone number.
        """
        if not is_valid_telephone_number(phone_number=value):
            raise ValueError(ErrorMessages.INVALID_PHONE_NUMBER.value)
        return value


class CreateUserProfileSchema(BaseUserProfileSchema):
    """Schema for request when creating a user profile."""

    user_id: str

    @field_validator("user_id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        """Check if the id is valid.

        Args:
            value (str): The id to validate.

        Returns:
            str: The validated id.
        """
        if not is_valid_uuid(uuid_to_test=value):
            raise ValueError(ErrorMessages.INVALID_ID.value)
        return value


UpdateUserProfileSchema = BaseUserProfileSchema


class UpdateUserProfileRequestSchema(BaseUserProfileSchema):
    """Schema for updating a user profile plus facility assignment."""

    facility_id: Optional[str] = None

    @field_validator("facility_id")
    @classmethod
    def validate_facility_id(cls, value: Optional[str]) -> Optional[str]:
        """Check if the facility id is valid."""
        if value is None:
            return value
        if not is_valid_uuid(uuid_to_test=value):
            raise ValueError(ErrorMessages.INVALID_ID.value)
        return value
