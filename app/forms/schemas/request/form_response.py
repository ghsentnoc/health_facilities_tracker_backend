from typing import Any, Optional

from pydantic import BaseModel, field_validator


class AnswerItemSchema(BaseModel):
    """Schema for a single answer in list format."""

    field_id: str
    value: Any


class CreateFormResponseRequestSchema(BaseModel):
    """Schema for creating a new form response (submission).

    Accepts answers in two formats:
    - Dict format: {"field_id_1": "value1", "field_id_2": "value2"}
    - List format: [{"field_id": "...", "value": "..."}]
    """

    form_id: str
    submitted_by: Optional[str] = None
    answers: Any

    @field_validator("answers", mode="before")
    @classmethod
    def normalize_answers(cls, value: Any) -> dict[str, Any]:
        """Normalize answers to dict format regardless of input format.

        Args:
            value: The raw answers value (dict or list).

        Returns:
            dict: Answers keyed by field_id.
        """
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            result: dict[str, Any] = {}
            for item in value:
                if isinstance(item, dict) and "field_id" in item:
                    result[item["field_id"]] = item.get("value")
                else:
                    raise ValueError("Each answer in list format must have 'field_id' and 'value' keys.")
            return result
        raise ValueError("Answers must be a dict (field_id→value) or a list of {field_id, value} objects.")
