from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.utils.constants import BASE_DIR


class DBConfig(BaseSettings):
    """Database configuration settings."""

    DB_HOST: str = "127.0.0.1"
    DB_DOCKER_HOST: str = "health-facilities-tracker-db"
    DB_DOCKER_PORT: int = 3306
    DB_DRIVER: str = "mysql+pymysql"

    # production
    DB_USER_PROD: str = ""
    DB_PASSWORD_PROD: str = ""
    DB_PORT_PROD: str = "3306"
    DB_NAME_PROD: str = ""

    # development
    DB_USER_DEV: str = ""
    DB_PASSWORD_DEV: str = ""
    DB_PORT_DEV: str = "3308"
    DB_NAME_DEV: str = ""

    # test
    DB_USER_TEST: str = ""
    DB_PASSWORD_TEST: str = ""
    DB_PORT_TEST: str = "3307"
    DB_NAME_TEST: str = ""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")


db_config = DBConfig()  # type: ignore
