from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.utils.constants import BASE_DIR


class RedisConfig(BaseSettings):
    """Configuration class for redis."""

    REDIS_HOST: str = "127.0.0.1"
    REDIS_DOCKER_HOST: str = "nurture-redis"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_PORT_PROD: int = 6379
    REDIS_PORT_DEV: int = 6379
    REDIS_PORT_TEST: int = 6379
    REDIS_DOCKER_PORT: int = 6379
    MAX_CONNECTION_POOL_SIZE: int = 10

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")


redis_config = RedisConfig()  # type: ignore
