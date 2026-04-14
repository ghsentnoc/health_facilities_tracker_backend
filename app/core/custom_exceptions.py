class ObjectAlreadyExistsException(Exception):
    """Exception for already existing objects."""


class FailedToSaveObjectException(Exception):
    """Exception for failure to save objects."""


class InvalidFilterError(Exception):
    """Exception for invalid filter passed."""


class InvalidFilterOperatorError(Exception):
    """Exception for invalid operator passed."""


class InvalidSortError(Exception):
    """Exception for invalid sort passed."""


class InvalidSortModeError(Exception):
    """Exception for invalid sort mode passed."""


class InvalidQueryParamsJSONFormatError(Exception):
    """Exception for invalid query parameters json format."""


class InvalidPaginationOptionError(Exception):
    """Exception for invalid pagination options."""


class InvalidPaginationValueError(Exception):
    """Exception for invalid pagination value."""


class EntityDoesNotExistsError(Exception):
    """Exception for when an entity does not exist."""


class InvalidPasswordError(Exception):
    """Exception for when a password is invalid."""


class InvalidEmailError(Exception):
    """Exception for when an email is invalid."""


class InvalidPhoneNumberError(Exception):
    """Exception for when a phone number is invalid."""


class ExpiredTokenError(Exception):
    """Exception for when a token is expired."""


class InvalidTokenError(Exception):
    """Exception for when a token is invalid."""


class FailedToSetDataInRedisError(Exception):
    """Exception for when setting data in Redis fails."""


class FailedToRetrieveDataFromRedisError(Exception):
    """Exception for when retrieving data from Redis fails."""


class FailedToDeleteDataFromRedisError(Exception):
    """Exception for when deleting data from Redis fails."""


class FacilityNotApprovedError(Exception):
    """Exception for when a facility is not approved."""
