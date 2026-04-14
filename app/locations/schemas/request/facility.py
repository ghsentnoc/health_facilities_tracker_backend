from typing import Optional

from pydantic import BaseModel, field_validator

from app.locations.utils.constants import FacilityOwnership, FacilityType


class BaseFacilitySchema(BaseModel):
    """Base schema for facility request and response."""

    name: str
    facility_type: str
    ownership: str
    ghana_post_address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    altitude: Optional[float] = None
    registration_number: Optional[str] = None

    @field_validator("facility_type")
    @classmethod
    def validate_facility_type(cls, value: str) -> str:
        """Check if the facility type is valid.

        Args:
            value (str): The facility type to check

        Returns:
            str: The validated facility type.
        """
        normalized_value = value.strip().lower()
        allowed_values = {facility_type.value.lower() for facility_type in FacilityType}
        if normalized_value in allowed_values:
            return normalized_value
        raise ValueError("Invalid facility type.")

    @field_validator("ownership")
    @classmethod
    def validate_ownership(cls, value: str) -> str:
        """Check if the facility ownership is valid.

        Args:
            value (str): The facility ownership to check.

        Returns:
            str: The validated facility ownership.
        """
        normalized_value = value.strip().lower()
        allowed_values = {ownership.value.lower() for ownership in FacilityOwnership}
        if normalized_value in allowed_values:
            return normalized_value
        raise ValueError("Invalid facility ownership.")


class BaseCreateFacilitySchema(BaseFacilitySchema):
    """Base schema for creating a new facility."""

    district_id: str


class CreateFacilityRequestSchema(BaseCreateFacilitySchema):
    """Schema for creating a new facility."""

    contact_numbers: Optional[list[str]] = None


CreateFacilitySchema = BaseCreateFacilitySchema

UpdateFacilityRequestSchema = CreateFacilityRequestSchema

UpdateFacilitySchema = BaseCreateFacilitySchema
