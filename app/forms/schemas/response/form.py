from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from app.core.schemas.base_read_schema import BaseReadSchema


class ReadFieldValidationSchema(BaseModel):
    """Schema for reading field validation rules."""

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min: Optional[float] = None
    max: Optional[float] = None
    regex: Optional[str] = None


class ReadFormFieldSchema(BaseReadSchema):
    """Schema for reading a form field."""

    section_id: str
    form_id: str
    label: str
    field_type: str
    required: bool
    placeholder: Optional[str] = None
    options: Optional[list[str]] = None
    validation: Optional[Any] = None
    default_value: Optional[str] = None
    order: int
    conditional_logic: Optional[Any] = None
    help_text: Optional[str] = None
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None


class ReadFormSectionSchema(BaseReadSchema):
    """Schema for reading a form section."""

    form_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    order: int
    fields: list[ReadFormFieldSchema] = []
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None


class ReadFormSchema(BaseReadSchema):
    """Schema for reading a form."""

    title: str
    description: Optional[str] = None
    created_by: Optional[str] = None
    status: str
    sections: list[ReadFormSectionSchema] = []
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None
