from enum import Enum
from pathlib import Path

from app.core.docs.main import project_description

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class ApplicationConstants(Enum):
    """Constants for the application."""

    APP_NAME = "Health Facilities Tracker"
    DESCRIPTION = project_description.format(app_name=APP_NAME)
    API_V1_STR = "/api/v1"
    API_V2_STR = "/api/v2"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ProjectEnvironmentConstants(Enum):
    """Constants for different project environments."""

    DEV = "DEV"
    PROD = "PROD"
    TEST = "TEST"


class ProjectPlatformConstants(Enum):
    """Constants for project platform."""

    LOCAL = "Local"
    DOCKER = "Docker"


class PaginationConstants(Enum):
    """Constants for pagination settings."""

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 25
    MAX_PAGE_SIZE = 50


class HTTPResponseStatus(Enum):
    """Enum for HTTP response status."""

    SUCCESS = "success"
    ERROR = "error"
