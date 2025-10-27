from datetime import datetime
from typing import Optional, Union

from pydantic import field_validator

from app.core.custom_exceptions import InvalidPhoneNumberError
from app.core.schemas.base_read_schema import BaseReadSchema
from app.core.utils.messages import ErrorMessages
from app.core.utils.validators import is_valid_telephone_number


class ReadUserSchema(BaseReadSchema):
    """Schema for user responses."""

    email: str
    first_name: str
    last_name: str
    phone_number: str
    country: str
    facility_name: str
    first_time_login: bool
    is_logout: bool
    last_login: Optional[datetime]
    is_verified: bool
    is_suspended: bool
    is_approved: bool

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        """Check if the phone number is valid.

        Args:
            value (str): The phone number to validate.

        Returns:
            str: The validated phone number.
        """
        if not is_valid_telephone_number(phone_number=value):
            raise InvalidPhoneNumberError(ErrorMessages.INVALID_PHONE_NUMBER.value)
        return value

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
