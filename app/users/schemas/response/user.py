from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, field_validator

from app.core.schemas.base_read_schema import BaseReadSchema
from app.users.schemas.request.user_profile import BaseUserProfileSchema


class ReadUserRoleSchema(BaseModel):
    """Schema for user roles."""

    id: str
    name: str


class ReadUserFacilitySchema(BaseModel):
    """Schema for nested facility details on a user response."""

    id: str
    name: str


class ReadUserSchema(BaseReadSchema):
    """Schema for user responses."""

    email: str
    profile: BaseUserProfileSchema
    facility: Optional[ReadUserFacilitySchema] = None
    first_time_login: bool
    is_logout: bool
    last_login: Optional[datetime]
    is_verified: bool
    is_suspended: bool
    is_approved: bool

    @field_validator("last_login")
    @classmethod
    def datetime_is_valid(cls, dt: Union[datetime, None]) -> Union[datetime, None]:
        """Validate that the given datetime is valid

        Args:
            dt (datetime): The datetime to validate

        Returns:
            datetime: The validated datetime
        """
        if dt is not None and isinstance(dt, datetime):
            return dt
        if dt is None:
            return None
