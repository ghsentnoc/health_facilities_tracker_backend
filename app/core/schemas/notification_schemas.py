from typing import Any

from pydantic import BaseModel, EmailStr, Field


class EmailNotificationMessageSchema(BaseModel):
    """Schema for email notification messages sent to RabbitMQ."""

    channel: str = "email"
    notification_type: str
    subject: str
    recipients: list[EmailStr]
    template_name: str
    body: dict[str, Any] = Field(default_factory=dict)
    cc: list[EmailStr] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SMSNotificationMessageSchema(BaseModel):
    """Schema for SMS notification messages sent to RabbitMQ."""

    channel: str = "sms"
    notification_type: str
    phone_numbers: list[str]
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PushNotificationMessageSchema(BaseModel):
    """Schema for push notification messages sent to RabbitMQ."""

    channel: str = "push"
    notification_type: str
    title: str
    body: str
    device_tokens: list[str]
    data: dict[str, Any] = Field(default_factory=dict)
