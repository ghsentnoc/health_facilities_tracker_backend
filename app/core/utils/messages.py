from enum import Enum
from typing import Optional, Type, TypeVar

T = TypeVar("T")


class ErrorMessages(Enum):
    """Constants for error messages."""

    NOT_VERIFIED = "This account is not verified."
    ALREADY_VERIFIED = "This account has already been verified."
    EXPIRED_TOKEN = "The token provided is expired."
    INVALID_TOKEN = "The token provided is not valid."
    INVALID_PHONE_NUMBER = (
        "The phone number is not valid. Phone numbers format: (country_code)number.\nE.g (233)111111111"
    )
    INVALID_EMAIL = "The email provided is not a valid email."
    INVALID_PASSWORD = (
        "The password provided is not a valid password. Passwords must be 8 or more characters, "
        "contain at least 1 uppercase, lowercase and number"
    )
    INVALID_ID = "The id provided is not of the right format."
    INVALID_PAGINATION_VALUES = "Pagination values must be positive integers."

    @classmethod
    def already_exists(cls, *, object_type: Type[T]) -> str:
        """Function to create already exists error messages.

        Args:
            object_type (Type[T]): The type of object.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} already exists."

    @classmethod
    def already_approved(cls, *, object_type: Type[T], value: str) -> str:
        """Function to create already approved error messages.

        Args:
            object_type (Type[T]): The type of object.
            value (str): The value that has already been approved.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} {value} has already been approved."

    @classmethod
    def entity_not_approved(cls, *, object_type: Type[T], value: str) -> str:
        """Function to create entity not approved error messages.

        Args:
            object_type (Type[T]): The type of object.
            value (str): The value that has not been approved.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} {value} has not been approved."

    @classmethod
    def entity_does_not_exists(cls, *, entity_type: Type[T], value: str) -> str:
        """Function to create entity does not exist error messages.

        Args:
              entity_type (str): The entity type.
              value (str): The value that do not exist.

        Returns:
             str: The message
        """
        return f"{entity_type.__name__} '{value}' does not exist."

    @classmethod
    def cannot_restore_existing_entity(cls, *, entity_type: Type[T], value: str) -> str:
        """Function to create cannot restore existing entity error messages.

        Args:
              entity_type (str): The entity type.
              value (str): The value that do not exist.

        Returns:
             str: The message
        """
        return f"Cannot restore existing {entity_type.__name__} '{value}'."

    @classmethod
    def invalid_filter_or_sort(cls, *, filter_or_sort_field: str) -> str:
        """Function to create invalid filter error message.

        Args:
            filter_or_sort_field (str): The name of the filter.

        Returns:
            str: The message
        """
        return f"{filter_or_sort_field} is not allowed or invalid."

    @classmethod
    def invalid_operator(cls, *, filter_name: str, operator: str) -> str:
        """Function to create invalid operator error message.

        Args:
            filter_name (str): The filter name the operator is being used on
            operator (str): The operator to use on filter

        Returns:
            str: The message
        """
        return f"{operator} cannot be used on {filter_name}."

    @classmethod
    def missing_required_query_param(cls, *, query_param: str) -> str:
        """Function to create missing required query param error message.

        Args:
            query_param (str): The name of the query param.

        Returns:
            str: The message
        """
        return f"Missing required query param: '{query_param}'."

    @classmethod
    def invalid_mode_for_sort(cls, *, sort_mode: str) -> str:
        """Function to create invalid mode for sort error message.

        Args:
            sort_mode (str): The mode of the sort.

        Returns:
            str: The message
        """
        return f"Invalid mode '{sort_mode}' for sort. Allowed modes are 'asc' and 'desc'."

    @classmethod
    def invalid_json_format_for_query_params(cls, *, query_param: str) -> str:
        """Function to create invalid json format for query params error message.

        Args:
            query_param (str): The name of the query param.

        Returns:
            str: The message
        """
        return f"Invalid JSON format for '{query_param}'. Please send valid JSON."


class SuccessMessages(Enum):
    """Constants for success messages."""

    PASSWORD_RESET_TOKEN_VERIFIED = "Password reset token verified successfully."
    PASSWORD_RESET = "Password reset successful."
    RESET_PASSWORD_EMAIL_SENT = "Reset password verification email sent successfully."
    VERIFICATION_EMAIL_SENT = "Account verification email sent successfully."
    VERIFIED = "The account has been verified successfully."

    @classmethod
    def created_successfully(cls, *, object_type: Type[T], extra_info: Optional[str] = None) -> str:
        """Function to create created successfully message.

        Args:
            object_type (Type[T]): The type of object.
            extra_info (str): The extra information to append ot the message.

        Returns:
            str: The message
        """
        return (
            f"{object_type.__name__} created successfully."
            if not extra_info
            else f"{object_type.__name__} created successfully."
        )

    @classmethod
    def updated_successfully(cls, *, object_type: Type[T]) -> str:
        """Function to create updated successfully message.

        Args:
            object_type (Type[T]): The type of object.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} updated successfully."

    @classmethod
    def deleted_successfully(cls, *, object_type: Type[T]) -> str:
        """Function to create deleted successfully message.

        Args:
            object_type (Type[T]): The type of object.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} deleted successfully."

    @classmethod
    def retrieved_successfully(cls, *, object_type: Type[T]) -> str:
        """Function to create retrieved successfully message.

        Args:
            object_type (Type[T]): The type of object.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} retrieved successfully."

    @classmethod
    def restored_successfully(cls, *, object_type: Type[T]) -> str:
        """Function to create restored successfully message.

        Args:
            object_type (Type[T]): The type of object.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} restored successfully."

    @classmethod
    def approved_successfully(cls, *, object_type: Type[T], value: str) -> str:
        """Function to create approved successfully message.

        Args:
            object_type (Type[T]): The type of object.
            value (str): The value approved successfully.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} {value} approved successfully."
