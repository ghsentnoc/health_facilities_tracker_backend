import logging

from app.core.config.rabbitmq_config import rabbitmq_config
from app.core.consumers.notification_consumers import NotificationConsumers
from app.core.services.rabbitmq_service import RabbitMQService, RabbitMQTopology
from app.core.utils.queues_exchanges_bindings import (
    email_notifications_queue,
    exchanges,
    push_notifications_queue,
    queue_bindings,
    queues,
    sms_notifications_queue,
)

logger = logging.getLogger(__name__)


class NotificationWorker:
    """Worker that consumes notification queues."""

    def __init__(self) -> None:
        """Initialize the notification worker."""
        self.rabbitmq_service = RabbitMQService(config=rabbitmq_config)
        self.topology = RabbitMQTopology(rabbitmq_service=self.rabbitmq_service)
        self.consumers = NotificationConsumers()

    def run(self) -> None:
        """Start the notification worker."""
        self.rabbitmq_service.connect()
        self.topology.setup_topology(exchanges=exchanges, queues=queues, bindings=queue_bindings)
        self.rabbitmq_service.channel.basic_qos(prefetch_count=1)

        self.rabbitmq_service.consume(
            queue_name=email_notifications_queue.name,
            callback_func=self.consumers.consume_email_notification,
        )
        self.rabbitmq_service.consume(
            queue_name=sms_notifications_queue.name,
            callback_func=self.consumers.consume_sms_notification,
        )
        self.rabbitmq_service.consume(
            queue_name=push_notifications_queue.name,
            callback_func=self.consumers.consume_push_notification,
        )

        logger.info("Notification worker started. Waiting for RabbitMQ messages.")
        try:
            self.rabbitmq_service.start_consuming()
        finally:
            self.rabbitmq_service.close()


def main() -> None:
    """Run the notification worker."""
    logging.basicConfig(level=logging.INFO)
    worker = NotificationWorker()
    worker.run()


if __name__ == "__main__":
    main()
