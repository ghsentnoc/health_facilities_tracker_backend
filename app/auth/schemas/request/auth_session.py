from typing import Literal

from pydantic import BaseModel, field_validator

from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_uuid


class CreateAuthSessionSchema(BaseModel):
    """Schema for creating a new auth session"""

    user_id: str
    token_version: int
    device_id: str
    client_type: Literal["web", "mobile", "api", "desktop", "cli"]

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, value: str) -> str:
        """Check if the user id is a valid uuid

        Args:
            value (str): The user id to validate

        Returns:
            str: The validated user id
        """
        if not is_valid_uuid(uuid_to_test=value):
            raise ValueError(ErrorMessages.INVALID_ID.value)
        return value
