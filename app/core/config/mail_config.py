from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.utils.constants import BASE_DIR


class MailConfig(BaseSettings):
    """Configurations for mail."""

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_FROM: str = "noreply@healthfacilities.gov.gh"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")


mail_config = MailConfig()  # type: ignore
