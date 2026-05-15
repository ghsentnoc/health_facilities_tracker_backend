from dataclasses import dataclass
from typing import Any, Literal


@dataclass(slots=True)
class RabbitMQExchange:
    """Data class for RabbitMQ exchange configuration."""

    name: str
    type: Literal["direct", "topic", "headers", "fanout"] = "direct"
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: dict[str, Any] | None = None


@dataclass(slots=True)
class RabbitMQQueue:
    """Data class for RabbitMQ queue configuration."""

    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: dict[str, Any] | None = None
    passive: bool = False
    queue_type: Literal["classic", "quorum"] = "classic"


@dataclass(slots=True)
class RabbitMQQueueBinding:
    """Data class for RabbitMQ binding configuration."""

    queue_name: str
    exchange_name: str
    routing_key: str = ""
    arguments: dict[str, Any] | None = None
