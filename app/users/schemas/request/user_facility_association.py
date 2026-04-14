from pydantic import BaseModel, field_validator

from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_uuid


class BaseUserFacilityAssociationSchema(BaseModel):
    """The base schema for user facility association operations."""

    facility_id: str

    @field_validator("facility_id")
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


class CreateUserFacilityAssociationSchema(BaseUserFacilityAssociationSchema):
    """The schema for creating a user facility association."""

    user_id: str

    @field_validator("facility_id")
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


UpdateUserFacilityAssociationSchema = BaseUserFacilityAssociationSchema
