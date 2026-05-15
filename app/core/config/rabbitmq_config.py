from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.config.project_config import project_config
from app.core.utils.constants import BASE_DIR, ProjectPlatformConstants


class RabbitMQConfig(BaseSettings):
    """Configuration for RabbitMQ connection."""

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_DOCKER_HOST: str
    RABBITMQ_VHOST: str = "/"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("RABBITMQ_VHOST", mode="before")
    @classmethod
    def normalize_vhost(cls, value: str | None) -> str:
        """Normalize the configured RabbitMQ virtual host."""
        if value is None or str(value).strip() == "":
            return "/"

        normalized_value = str(value).strip()
        if normalized_value == "/":
            return normalized_value

        return normalized_value if normalized_value.startswith("/") else f"/{normalized_value}"

    def get_resolved_host(self) -> str:
        """Get the resolved RabbitMQ host based on the project platform.

        Returns:
            str: The resolved RabbitMQ host.
        """
        if str(project_config.PROJECT_PLATFORM).lower() == ProjectPlatformConstants.DOCKER.value.lower():
            return self.RABBITMQ_DOCKER_HOST or self.RABBITMQ_HOST
        return self.RABBITMQ_HOST


rabbitmq_config = RabbitMQConfig()  # type: ignore
