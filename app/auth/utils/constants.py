from enum import Enum


class RoleConstants(Enum):
    """Enum for roles."""

    ADMIN = "admin"
    FACILITY_REP = "facility-rep"
    SUPER_ADMIN = "super-admin"


class TokenTypeConstants(Enum):
    """Enum for token types."""

    ACCESS_TOKEN = "access-token"
    REFRESH_TOKEN = "refresh-token"
    ACCOUNT_VERIFICATION_TOKEN = "account-verification-token"
    PASSWORD_RESET_TOKEN = "password-reset-token"
