from typing import Literal, Union

from pydantic import BaseModel, Field, field_validator

from app.core.utils.constants import PaginationConstants


class AllowedFilterSchema(BaseModel):
    """The schema for allowed filters."""

    field: str
    operators: list[Literal["eq", "gt", "ge", "lt", "le", "ne", "like"]] = Field(default=["eq"])

    @field_validator("operators", mode="before")
    @classmethod
    def validate_operators(cls, value: list[str]) -> list[str]:
        """Validate allowed operators and convert all to lowercase.

        Args:
            value (Optional[list[str]]): The list of operators to validate and convert.

        Returns:
            list[str]: The validated and converted operators
        """
        if value is not None:
            return [operator.lower() for operator in value]
        return ["eq"]


class FilterSchema(BaseModel):
    """The schema for the filters."""

    value: Union[str, int]
    operator: str = "eq"

    @field_validator("operator", mode="before")
    @classmethod
    def validate_operator(cls, value: str) -> str:
        """Validate and convert operator to lowercase.

        Args:
            value (str): The operator value to validate and convert.

        Returns:
            str: The validated and converted operator.
        """
        if value is None:
            return "eq"
        return value.lower()

    @field_validator("value", mode="before")
    @classmethod
    def convert_value_to_int_if_digit(cls, value: str) -> str | int:
        """Convert value to int if it's a digit.

        Args:
            value (str): The value to convert.

        Returns:
            str | int: The converted value.
        """
        if str(value).isdigit():
            return int(value)
        return value


class AllowedSortSchema(BaseModel):
    """The schema for allowed sorts."""

    field: str
    mode: list[Literal["asc", "desc"]] = Field(default=["asc", "desc"])

    @field_validator("mode", mode="before")
    @classmethod
    def validate_mode(cls, value: list[str]) -> list[str]:
        """Validate and convert mode to lowercase.

        Args:
            value (list[str]): The mode value to validate and convert.

        Returns:
            str: The validated and converted mode.
        """
        if value is not None:
            return [m.lower() for m in value]
        return ["asc", "desc"]


class PaginationSchema(BaseModel):
    """The schema for pagination."""

    page: int = Field(default=PaginationConstants.DEFAULT_PAGE.value, ge=1)
    page_size: int = Field(
        default=PaginationConstants.DEFAULT_PAGE_SIZE.value, ge=1, le=PaginationConstants.MAX_PAGE_SIZE.value
    )

    @field_validator("page", "page_size", mode="before")
    @classmethod
    def convert_to_int_if_digit(cls, value: str) -> int:
        """Convert value to int if it's a digit.

        Args:
            value (str): The value to convert.

        Returns:
            int: The converted value.
        """
        if str(value).isdigit() and int(value) >= 1:
            return int(value)
        return 1


class JoinedSortSchema(BaseModel):
    """The schema for joined sorts."""

    field: str
    model: str
    direction: str

    @field_validator("direction", mode="before")
    @classmethod
    def validate_mode(cls, value: str) -> str:
        """Validate and convert mode to lowercase.

        Args:
            value (list[str]): The mode value to validate and convert.

        Returns:
            str: The validated and converted mode.
        """
        if value is not None and value.strip().lower() in ["asc", "desc"]:
            return value.strip().lower()
        return "asc"
