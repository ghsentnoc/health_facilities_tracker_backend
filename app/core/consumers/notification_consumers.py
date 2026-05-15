import asyncio
import json
import logging

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pydantic import ValidationError

from app.core.schemas.notification_schemas import (
    EmailNotificationMessageSchema,
    PushNotificationMessageSchema,
    SMSNotificationMessageSchema,
)
from app.core.services.mail_service import MailServiceBuilder
from app.core.services.push_notification_service import PushNotificationService
from app.core.services.sms_service import SMSService

logger = logging.getLogger(__name__)


class NotificationConsumers:
    """Consumers for notification queues."""

    def __init__(self) -> None:
        """Initialize notification consumers."""
        self.sms_service = SMSService()
        self.push_notification_service = PushNotificationService()

    def consume_email_notification(
        self,
        channel: BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Consume and process email notification messages."""
        del properties
        try:
            message = EmailNotificationMessageSchema.model_validate(json.loads(body.decode("utf-8")))
            asyncio.run(self._send_email(message=message))
        except (ValidationError, json.JSONDecodeError, RuntimeError, Exception):
            logger.exception("Failed to process email notification message")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume_sms_notification(
        self,
        channel: BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Consume and process SMS notification messages."""
        del properties
        try:
            message = SMSNotificationMessageSchema.model_validate(json.loads(body.decode("utf-8")))
            self.sms_service.send_sms(
                phone_numbers=message.phone_numbers,
                message=message.message,
                metadata=message.metadata,
            )
        except (ValidationError, json.JSONDecodeError, Exception):
            logger.exception("Failed to process SMS notification message")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume_push_notification(
        self,
        channel: BlockingChannel,
        method: pika.spec.Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        """Consume and process push notification messages."""
        del properties
        try:
            message = PushNotificationMessageSchema.model_validate(json.loads(body.decode("utf-8")))
            self.push_notification_service.send_push_notification(
                device_tokens=message.device_tokens,
                title=message.title,
                body=message.body,
                data=message.data,
            )
        except (ValidationError, json.JSONDecodeError, Exception):
            logger.exception("Failed to process push notification message")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)

    async def _send_email(self, *, message: EmailNotificationMessageSchema) -> None:
        """Send an email notification."""
        mail_service = MailServiceBuilder()
        (
            mail_service.subject(subject=message.subject)
            .recipients(recipients=list(message.recipients))  # type: ignore[arg-type]
            .cc(cc=list(message.cc))  # type: ignore[arg-type]
            .template(template_name=message.template_name)
            .body(body=message.body)
        )
        await mail_service.send_mail()
