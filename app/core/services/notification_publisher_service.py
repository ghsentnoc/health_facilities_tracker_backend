import logging

from app.core.config.rabbitmq_config import rabbitmq_config
from app.core.schemas.notification_schemas import (
    EmailNotificationMessageSchema,
    PushNotificationMessageSchema,
    SMSNotificationMessageSchema,
)
from app.core.services.rabbitmq_service import RabbitMQService, RabbitMQTopology
from app.core.utils.queues_exchanges_bindings import (
    NotificationRoutingKeys,
    exchanges,
    notifications_exchange,
    queue_bindings,
    queues,
)

logger = logging.getLogger(__name__)


class NotificationPublisherService:
    """Service for publishing notifications to RabbitMQ."""

    def __init__(self) -> None:
        """Initialize the publisher service."""
        self._rabbitmq_service = RabbitMQService(config=rabbitmq_config)

    def publish_email_notification(self, *, message: EmailNotificationMessageSchema) -> None:
        """Publish an email notification message."""
        self._publish(
            routing_key=NotificationRoutingKeys.EMAIL,
            message=message.model_dump_json(),
        )

    def publish_sms_notification(self, *, message: SMSNotificationMessageSchema) -> None:
        """Publish an SMS notification message."""
        self._publish(
            routing_key=NotificationRoutingKeys.SMS,
            message=message.model_dump_json(),
        )

    def publish_push_notification(self, *, message: PushNotificationMessageSchema) -> None:
        """Publish a push notification message."""
        self._publish(
            routing_key=NotificationRoutingKeys.PUSH,
            message=message.model_dump_json(),
        )

    def _publish(self, *, routing_key: str, message: str) -> None:
        """Publish a notification message after ensuring topology exists."""
        self._rabbitmq_service.connect()
        try:
            topology = RabbitMQTopology(rabbitmq_service=self._rabbitmq_service)
            topology.setup_topology(exchanges=exchanges, queues=queues, bindings=queue_bindings)
            logger.info(
                "Publishing notification message to exchange=%s routing_key=%s vhost=%s",
                notifications_exchange.name,
                routing_key,
                rabbitmq_config.RABBITMQ_VHOST,
            )
            self._rabbitmq_service.publish(
                exchange_name=notifications_exchange.name,
                routing_key=routing_key,
                message=message,
                persistent=True,
            )
        finally:
            self._rabbitmq_service.close()
