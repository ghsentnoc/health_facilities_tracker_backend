from enum import Enum
from typing import Optional, Type, TypeVar

T = TypeVar("T")


class ErrorMessages(Enum):
    """Constants for error messages."""

    FACILITY_REPRESENTATIVE_LIMIT_EXCEEDED = "A facility can only have 4 representatives."
    INVALID_OAUTH_STATE = "Invalid OAuth state parameter."
    INVALID_URL = "The URL provided is not valid."
    INVALID_DOMAIN_ASSOCIATION = "The domain id provided is not associated with the user's domain."
    UNAUTHENTICATED_APP = "Application is not authenticated."
    UNAUTHORIZED_APP = "Application (Key) is not authorized."
    ALREADY_ACTIVATED = "Application is already activated."
    ALREADY_DEACTIVATED = "Application is already deactivated."
    INACTIVE_APPLICATION = "Application is not active."
    ACCOUNT_SUSPENDED = "This account has been suspended."
    NO_PASSWORD = "This account was created without a password. Please set one to continue."
    PASSWORD_ALREADY_SET = "Account already set up."
    INVALID_CREDENTIALS = "The credentials provided are not valid."
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
    UNAUTHORIZED_USER = "User is not authorized."
    UNAUTHENTICATED_USER = "user is not authenticated."

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
    def already_licensed(cls, *, object_type: Type[T], value: str) -> str:
        """Function to create already licensed error messages.

        Args:
            object_type (Type[T]): The type of object.
            value (str): The value that has already been licensed.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} {value} has already been licensed."

    @classmethod
    def entity_exists_but_deleted(cls, *, entity_type: Type[T], value: str) -> str:
        """Function to create entity exists but deleted error messages.

        Args:
            entity_type (Type[T]): The type of entity.
            value (str): The value of the entity that exists but is deleted.

        Returns:
            str: The message
        """
        return f"{entity_type.__name__} '{value}' already exists but is deleted."

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
              value (str): The value that does not exist.

        Returns:
             str: The message
        """
        return f"{entity_type.__name__} '{value}' does not exist."

    @classmethod
    def cannot_restore_existing_entity(cls, *, entity_type: Type[T], value: str) -> str:
        """Function to create cannot restore existing entity error messages.

        Args:
              entity_type (str): The entity type.
              value (str): The value that does not exist.

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

    @classmethod
    def required_field(cls, *, field_name: str) -> str:
        """Function to create required field error message.

        Args:
            field_name (str): The name of the field.

        Returns:
            str: The message
        """
        return f"{field_name} is a required field."

    @classmethod
    def cannot_update_profile(cls) -> str:
        """Function to create cannot update profile error message.

        Returns:
            str: The message.
        """
        return (
            "You are not assigned any health professional role. You cannot update this profile. "
            "Please contact your administrator to have your role updated."
        )


class SuccessMessages(Enum):
    """Constants for success messages."""

    AUTHORIZATION_URL_GENERATED = "Authorization URL generated successfully."
    ROLE_SWITCHED_SUCCESSFULLY = "Role switched successfully."
    ACCOUNT_SUSPENDED_SUCCESSFULLY = "Account suspended successfully."
    ACCOUNT_REACTIVATED_SUCCESSFULLY = "Account reactivated successfully."
    TOKENS_REVOKED_SUCCESSFULLY = "Tokens revoked successfully."
    API_KEYS_REVOKED_SUCCESSFULLY = "Api keys revoked successfully."
    API_KEY_ROTATED_SUCCESSFULLY = "Api key rotated successfully."
    APPLICATION_DEACTIVATED = "Application deactivated successfully."
    APPLICATION_ACTIVATED = "Application activated successfully."
    AUTHENTICATED = "Authenticated successfully."
    LOGOUT = "Logged out successfully."
    PASSWORD_RESET_TOKEN_VERIFIED = "Password reset token verified successfully."
    PASSWORD_RESET = "Password reset successful."
    PASSWORD_SET_SUCCESSFULLY = "Password has been set successfully. Proceed to login."
    PASSWORD_CHANGED_SUCCESSFULLY = "Password has been changed successfully."
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

    @classmethod
    def licensed_successfully(cls, *, object_type: Type[T], value: str) -> str:
        """Function to create license successfully message.

        Args:
            object_type (Type[T]): The type of object.
            value (str): The value licensed successfully.

        Returns:
            str: The message
        """
        return f"{object_type.__name__} {value} licensed successfully."
