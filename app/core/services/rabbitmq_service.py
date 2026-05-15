from functools import partial
from typing import Callable

from pika import BasicProperties, BlockingConnection, ConnectionParameters, DeliveryMode, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel

from app.core.config.rabbitmq_config import RabbitMQConfig
from app.core.custom_exceptions import RabbitMQServiceError
from app.core.schemas.rabbitmq_schemas import RabbitMQExchange, RabbitMQQueue, RabbitMQQueueBinding
from app.core.utils.messages import ErrorMessages


class RabbitMQService:
    """Service for managing RabbitMQ connections and operations."""

    def __init__(self, config: RabbitMQConfig) -> None:
        """Initializer for the RabbitMQ service.

        Args:
            config (RabbitMQConfig): The RabbitMQ configuration.
        """
        self._host = config.get_resolved_host()
        self._port = config.RABBITMQ_PORT
        self._username = config.RABBITMQ_USER
        self._password = config.RABBITMQ_PASSWORD
        self._vhost = config.RABBITMQ_VHOST
        self._connection: BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    @property
    def channel(self) -> BlockingChannel:
        """Get the RabbitMQ channel.

        Returns:
            BlockingChannel: The RabbitMQ channel.
        """
        # check if channel exists or not
        if self._channel is None:
            raise RabbitMQServiceError(ErrorMessages.CHANNEL_NOT_INITIALIZED.value)
        return self._channel

    @property
    def connection(self) -> BlockingConnection:
        """Get the RabbitMQ connection.

        Returns:
            BlockingConnection: The RabbitMQ connection.
        """
        # check if connection exists or not
        if self._connection is None:
            raise RabbitMQServiceError(ErrorMessages.CONNECTION_NOT_INITIALIZED.value)
        return self._connection

    def connect(self) -> None:
        """Establish a connection to RabbitMQ and return a channel."""
        # create connection parameters
        connection_parameters = ConnectionParameters(
            host=self._host,
            port=self._port,
            virtual_host=self._vhost,
            credentials=PlainCredentials(username=self._username, password=self._password),
        )

        # check if connection is already opened.
        if self._connection and self._connection.is_open:
            self._connection.close()

        self._connection = BlockingConnection(parameters=connection_parameters)  # create connection
        self._channel = self._connection.channel()  # type: ignore  # create channel

    def close(self) -> None:
        """Close the RabbitMQ connection."""
        # close connection
        if self._connection and self._connection.is_open:
            self._connection.close()

    def publish(self, *, exchange_name: str, routing_key: str, message: str | bytes, persistent: bool = False) -> None:
        """Publish a message to RabbitMQ.

        Args:
            exchange_name (str): The name of the exchange to publish the message to.
            routing_key (str): The routing key to use for the message.
            message (str | bytes): The message to publish.
            persistent (bool): Whether the message should be marked as persistent. Defaults to False.
        """
        body = message if isinstance(message, bytes) else message.encode(encoding="utf-8")

        if persistent:
            properties = BasicProperties(delivery_mode=DeliveryMode.Persistent)  # Mark message as persistent
        else:
            properties = None

        self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=body, properties=properties)

    def consume(
        self,
        *,
        queue_name: str,
        callback_func: Callable,
        callback_args: dict | None = None,
        consumer_tag: str | None = None,
    ) -> None:
        """Consume messages from RabbitMQ.

        Args:
            queue_name (str): The name of the queue to consume messages from.
            callback_func (Callable): The callback function to process the consumed messages.
            callback_args (dict): The arguments to pass to the callback function.
            consumer_tag (str | None): An optional consumer tag to identify the consumer. Defaults to None.
        """
        callback_args = callback_args or {}
        partial_callback = partial(callback_func, **callback_args)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=partial_callback,
            auto_ack=False,
            consumer_tag=consumer_tag if consumer_tag else f"{queue_name}_consumer",
        )

    def start_consuming(self) -> None:
        """Start consuming messages from RabbitMQ."""
        self.channel.start_consuming()

    def stop_consuming(self) -> None:
        """Stop consuming messages from RabbitMQ."""
        self.channel.stop_consuming()


class RabbitMQTopology:
    """Class for managing RabbitMQ topology (exchanges, queues, bindings)."""

    def __init__(self, rabbitmq_service: RabbitMQService) -> None:
        """Initializer for the RabbitMQ topology manager.

        Args:
            rabbitmq_service (RabbitMQService): The RabbitMQ service instance to use for managing connections and
            channels.
        """
        self._rabbitmq_service = rabbitmq_service

    def setup_topology(
        self, exchanges: list[RabbitMQExchange], queues: list[RabbitMQQueue], bindings: list[RabbitMQQueueBinding]
    ) -> None:
        """Set up the RabbitMQ topology by declaring exchanges, queues, and bindings.

        Args:
            exchanges (list[RabbitMQExchange]): A list of RabbitMQExchange objects representing the exchanges to
            declare.
            queues (list[RabbitMQQueue]): A list of RabbitMQQueue objects representing the queues to declare.
            bindings (list[RabbitMQQueueBinding]): A list of RabbitMQQueueBinding objects representing the bindings to
            declare.
        """
        self._declare_exchanges(exchanges=exchanges)
        self._declare_queues(queues=queues)
        self._declare_bindings(bindings=bindings)

    def _declare_exchanges(self, *, exchanges: list[RabbitMQExchange]) -> None:
        """Declare RabbitMQ exchanges.

        Args:
            exchanges (list[RabbitMQExchange]): A list of RabbitMQExchange objects representing the exchanges to
            declare.
        """
        channel = self._rabbitmq_service.channel
        for exchange in exchanges:
            channel.exchange_declare(
                exchange=exchange.name,
                exchange_type=exchange.type,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
                internal=exchange.internal,
                arguments=exchange.arguments,
            )

    def _declare_queues(self, *, queues: list[RabbitMQQueue]) -> None:
        """Declare RabbitMQ queues.

        Args:
            queues (list[RabbitMQQueue]): A list of RabbitMQQueue objects representing the queues to declare.
        """
        channel = self._rabbitmq_service.channel
        for queue in queues:
            arguments = queue.arguments or {}
            if queue.queue_type == "quorum":
                arguments["x-queue-type"] = "quorum"
            else:
                arguments["x-queue-type"] = "classic"

            channel.queue_declare(
                queue=queue.name,
                durable=queue.durable,
                exclusive=queue.exclusive,
                auto_delete=queue.auto_delete,
                arguments=arguments,
                passive=queue.passive,
            )

    def _declare_bindings(self, *, bindings: list[RabbitMQQueueBinding]) -> None:
        """Declare RabbitMQ bindings.

        Args:
            bindings (list[RabbitMQQueueBinding]): A list of RabbitMQQueueBinding objects representing the bindings to
            declare.
        """
        channel = self._rabbitmq_service.channel
        for binding in bindings:
            channel.queue_bind(
                queue=binding.queue_name,
                exchange=binding.exchange_name,
                routing_key=binding.routing_key,
                arguments=binding.arguments,
            )

    def delete_queue(self, *, queue_name: str) -> None:
        """Delete a RabbitMQ queue.

        Args:
            queue_name (str): The name of the queue to delete.
        """
        self._rabbitmq_service.channel.queue_delete(queue=queue_name)

    def delete_exchange(self, *, exchange_name: str) -> None:
        """Delete a RabbitMQ exchange.

        Args:
            exchange_name (str): The name of the exchange to delete.
        """
        self._rabbitmq_service.channel.exchange_delete(exchange=exchange_name)

    def unbind_queue(self, *, queue_name: str, exchange_name: str, routing_key: str = "") -> None:
        """Unbind a RabbitMQ queue from an exchange.

        Args:
            queue_name (str): The name of the queue to unbind.
            exchange_name (str): The name of the exchange to unbind from.
            routing_key (str): The routing key used for the binding. Defaults to an empty string.
        """
        self._rabbitmq_service.channel.queue_unbind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
