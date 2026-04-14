from pydantic import BaseModel


class BaseApplicationSchema(BaseModel):
    """Schema for base application."""

    app_name: str
    platform: str


class CreateApplicationSchema(BaseApplicationSchema):
    """Schema for base application."""

    user_id: str


CreateApplicationRequestSchema = BaseApplicationSchema

UpdateApplicationSchema = CreateApplicationRequestSchema


class BaseAPIKeySchema(BaseModel):
    """Schema for base api key."""

    application_id: str
    api_key_id: str
    api_key_hash: str


CreateAPIKeySchema = BaseAPIKeySchema

UpdateAPIKeySchema = CreateAPIKeySchema
