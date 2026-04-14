from typing import Optional

from app.auth.schemas.request.applications_api_key import BaseApplicationSchema


class ReadApplicationSchema(BaseApplicationSchema):
    """Schema for read response of application."""

    id: str
    api_key: Optional[str] = None
