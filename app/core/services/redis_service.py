from typing import Any, Optional

from redis import Redis

from app.core.custom_exceptions import (
    FailedToDeleteDataFromRedisError,
    FailedToRetrieveDataFromRedisError,
    FailedToSetDataInRedisError,
)


class RedisService:
    """Service class for interacting with Redis."""

    def __init__(self, redis_client: Redis) -> None:
        """Initializer for RedisService.

        Args:
            redis_client (Redis): The Redis client instance.
        """
        self.redis_client = redis_client

    def set_data(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """Set data in Redis.

        Args:
            key (str): The key under which the data will be stored.
            value (Any): The value to be stored.
            expire (Optional[int]): Expiration time in seconds. If None, the data will not expire.
        """
        try:
            self.redis_client.set(name=key, value=value, ex=expire)
        except Exception as e:
            raise FailedToSetDataInRedisError(f"Failed to set data in Redis: {e}") from e

    def get_data(self, key: str) -> Optional[Any]:
        """Get data from Redis.

        Args:
            key (str): The key of the data to retrieve.

        Returns:
            Optional[Any]: The value associated with the key, or None if the key does not exist.
        """
        try:
            return self.redis_client.get(name=key)
        except Exception as e:
            raise FailedToRetrieveDataFromRedisError(f"Failed to retrieve data from Redis: {e}") from e

    def delete_data(self, key: str) -> None:
        """Delete data from Redis.

        Args:
            key (str): The key of the data to delete.
        """
        try:
            self.redis_client.delete(key)
        except Exception as e:
            raise FailedToDeleteDataFromRedisError(f"Failed to delete data from Redis: {e}") from e
