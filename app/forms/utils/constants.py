from enum import Enum


class FormStatus(Enum):
    """Enum for form statuses."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FieldType(Enum):
    """Enum for form field types."""

    TEXT = "text"
    NUMBER = "number"
    TEXTAREA = "textarea"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DATE = "date"
