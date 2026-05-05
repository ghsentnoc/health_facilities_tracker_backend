from datetime import datetime
from typing import Any, Optional

from app.core.schemas.base_read_schema import BaseReadSchema


class ReadFormResponseSchema(BaseReadSchema):
    """Schema for reading a form response (submission)."""

    form_id: str
    submitted_by: Optional[str] = None
    answers: dict[str, Any]
    submitted_at: datetime
    is_deleted: Optional[bool] = None
    deleted_at: Optional[datetime] = None
