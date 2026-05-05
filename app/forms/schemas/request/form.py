from typing import Any, Optional

from pydantic import BaseModel, field_validator

from app.forms.utils.constants import FieldType, FormStatus


class FieldValidationSchema(BaseModel):
    """Schema for field validation rules."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min: Optional[float] = None
    max: Optional[float] = None
    regex: Optional[str] = None


class CreateFormFieldRequestSchema(BaseModel):
    """Schema for creating a new form field."""

    label: str
    field_type: str
    required: bool = False
    placeholder: Optional[str] = None
    options: Optional[list[str]] = None
    validation: Optional[FieldValidationSchema] = None
    default_value: Optional[str] = None
    order: int = 0
    conditional_logic: Optional[dict[str, Any]] = None
    help_text: Optional[str] = None

    @field_validator("field_type")
    @classmethod
    def validate_field_type(cls, value: str) -> str:
        """Validate that the field type is allowed.

        Args:
            value (str): The field type to validate.

        Returns:
            str: The validated field type.
        """
        normalized = value.strip().lower()
        allowed = {ft.value for ft in FieldType}
        if normalized in allowed:
            return normalized
        raise ValueError(f"Invalid field type. Allowed types: {', '.join(allowed)}")


class UpdateFormFieldRequestSchema(BaseModel):
    """Schema for updating an existing form field."""

    label: Optional[str] = None
    field_type: Optional[str] = None
    required: Optional[bool] = None
    placeholder: Optional[str] = None
    options: Optional[list[str]] = None
    validation: Optional[FieldValidationSchema] = None
    default_value: Optional[str] = None
    order: Optional[int] = None
    conditional_logic: Optional[dict[str, Any]] = None
    help_text: Optional[str] = None

    @field_validator("field_type")
    @classmethod
    def validate_field_type(cls, value: Optional[str]) -> Optional[str]:
        """Validate that the field type is allowed.

        Args:
            value (str): The field type to validate.

        Returns:
            str: The validated field type.
        """
        if value is None:
            return value
        normalized = value.strip().lower()
        allowed = {ft.value for ft in FieldType}
        if normalized in allowed:
            return normalized
        raise ValueError(f"Invalid field type. Allowed types: {', '.join(allowed)}")


class CreateFormSectionRequestSchema(BaseModel):
    """Schema for creating a new form section."""

    title: Optional[str] = None
    description: Optional[str] = None
    order: int = 0
    fields: Optional[list[CreateFormFieldRequestSchema]] = None


class UpdateFormSectionRequestSchema(BaseModel):
    """Schema for updating an existing form section."""

    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None


class CreateFormRequestSchema(BaseModel):
    """Schema for creating a new form."""

    title: str
    description: Optional[str] = None
    status: str = "draft"
    sections: Optional[list[CreateFormSectionRequestSchema]] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """Validate that the form status is allowed.

        Args:
            value (str): The status to validate.

        Returns:
            str: The validated status.
        """
        normalized = value.strip().lower()
        allowed = {fs.value for fs in FormStatus}
        if normalized in allowed:
            return normalized
        raise ValueError(f"Invalid status. Allowed values: {', '.join(allowed)}")


class UpdateFormRequestSchema(BaseModel):
    """Schema for updating an existing form."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: Optional[str]) -> Optional[str]:
        """Validate that the form status is allowed.

        Args:
            value (str): The status to validate.

        Returns:
            str: The validated status.
        """
        if value is None:
            return value
        normalized = value.strip().lower()
        allowed = {fs.value for fs in FormStatus}
        if normalized in allowed:
            return normalized
        raise ValueError(f"Invalid status. Allowed values: {', '.join(allowed)}")
