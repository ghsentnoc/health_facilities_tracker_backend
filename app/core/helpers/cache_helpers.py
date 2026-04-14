import json
from typing import Any, Callable, Optional

from app.core.services.redis_service import RedisService


def get_cached_records(redis_service: RedisService, cache_key: str) -> Optional[list[dict[str, Any]]]:
    """Return cached records for a given key."""
    cached_data = redis_service.get_data(key=cache_key)
    return json.loads(cached_data) if cached_data else None


def set_cached_records(
    redis_service: RedisService,
    cache_key: str,
    records: list[dict[str, Any]],
    expire: Optional[int] = None,
) -> None:
    """Cache a list of serialized records."""
    redis_service.set_data(key=cache_key, value=json.dumps(records, default=str), expire=expire)


def invalidate_cache(redis_service: RedisService, cache_key: str) -> None:
    """Remove cached data for the given key."""
    redis_service.delete_data(key=cache_key)


def serialize_records(records: list, serializer: Callable[[Any], dict[str, Any]]) -> list[dict[str, Any]]:
    """Serialize a list of records using a serializer function."""
    return [serializer(record) for record in records]
