from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BaseRefreshTokenSchema(BaseModel):
    """Base schema for refresh token."""

    revoked: bool
    revoked_at: Optional[datetime] = None
    replaced_by_token: Optional[str] = None
    revoked_reason: Optional[str] = None


class CreateRefreshTokenSchema(BaseRefreshTokenSchema):
    """Schema for refresh token request."""

    user_id: str
    token: str
    token_id: str
    expires_at: datetime


class UpdateRefreshTokenSchema(BaseRefreshTokenSchema):
    """Schema for refresh token update request."""
