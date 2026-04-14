from app.core.schemas.base_read_schema import BaseReadSchema
from app.users.schemas.request.user_profile import BaseUserProfileSchema


class ReadUserProfileSchema(BaseReadSchema, BaseUserProfileSchema):
    """Schema for user profile response."""
