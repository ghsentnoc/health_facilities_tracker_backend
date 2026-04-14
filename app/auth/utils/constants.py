from enum import Enum


class PermissionConstants(Enum):
    """Enum for permissions."""

    # BYPASS JURISDICTION PERMISSION
    BYPASS_JURISDICTION = "bypass_jurisdiction"

    # USER RESOURCE PERMISSIONS
    LIST_USERS = "user.list"
    VIEW_USER = "user.view"
    UPDATE_USER = "user.update"
    DELETE_USER = "user.delete"
    RESTORE_USER = "user.restore"

    # PROFILE PERMISSIONS
    UPDATE_PROFILE = "profile.update"

    # ROLE PERMISSIONS
    LIST_ROLES = "role.list"
    VIEW_ROLE = "role.view"
    CREATE_ROLE = "role.create"
    UPDATE_ROLE = "role.update"
    DELETE_ROLE = "role.delete"
    RESTORE_ROLE = "role.restore"

    # PERMISSION PERMISSIONS
    LIST_PERMISSIONS = "permission.list"

    # APPLICATION PERMISSIONS
    LIST_APPLICATIONS = "application.list"
    VIEW_APPLICATION = "application.view"
    CREATE_APPLICATION = "application.create"
    UPDATE_APPLICATION = "application.update"
    ROTATE_APPLICATION_KEYS = "application_keys.rotate"
    REVOKE_APPLICATION_KEYS = "application_keys.revoke"
    DELETE_APPLICATION = "application.delete"
    RESTORE_APPLICATION = "application.restore"
    ACTIVATE_APPLICATION = "application.activate"
    DEACTIVATE_APPLICATION = "application.deactivate"

    # AUTHENTICATION PERMISSIONS
    CHANGE_USER_PASSWORD = "user_password.change"
    REVOKE_USER_TOKENS = "user_tokens.revoke"
    SUSPEND_USER_ACCOUNT = "user_account.suspend"
    REACTIVATE_USER_ACCOUNT = "user_account.reactivate"
    UPDATE_USER_ROLES = "user_roles.update"
    SWITCH_USER_ROLE = "user_role.switch"
    LOGOUT_USER = "user.logout"


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


class RefreshTokenRevocationReasons(Enum):
    """Enum for refresh token revocation reasons."""

    USER_LOGOUT_ALL_SESSIONS = "user-logout-all-sessions"
    USER_LOGOUT = "user-logout"
    TOKEN_ROTATION = "token-rotation"
    MANUAL_ADMIN_REVOKE = "manual-admin-revoke"
    TOKEN_COMPROMISED = "token-compromised"
    USER_PASSWORD_CHANGED = "user-password-changed"
    SESSION_EXPIRED = "session-expired"
    TOKEN_REUSE_DETECTED = "token-reuse-detected"
    MALFORMED_REQUEST = "malformed-request"
    USER_ACCOUNT_DEACTIVATED = "user-account-deactivated"
    SYSTEM_POLICY_UPDATE = "system-policy-update"
    USER_REAUTHENTICATED = "user-reauthenticated"


class APIKeyRevocationReasonConstants(Enum):
    """Enum for api revocation reasons"""

    APPLICATION_DELETED = "deleted"
    COMPROMISED = "compromised"
    USER_REQUEST = "user-request"
    ADMIN_REVOCATION = "admin-revocation"
    ROTATION = "rotation"
    EXPIRED = "expired"
    APPLICATION_DEACTIVATED = "application-deactivated"
    SUSPICIOUS_ACTIVITY = "suspicious-activity"
    POLICY_VIOLATION = "policy-violation"
    UNAUTHORIZED_USAGE = "unauthorized-usage"


class AppPlatformConstants(Enum):
    """Enum for application platform constants."""

    MOBILE = "mobile"
    WEB = "web"
    API_SERVICE = "api-service"


INTERNAL_APPLICATIONS = {
    "health-facilities-tracker-mobile": AppPlatformConstants.MOBILE.value,
    "health-facilities-tracker-web": AppPlatformConstants.WEB.value,
}

INTERNAL_APPLICATION_ALLOWED_ROLES = {
    "health-facilities-tracker-mobile": {RoleConstants.FACILITY_REP.value},
    "health-facilities-tracker-web": {
        RoleConstants.ADMIN.value,
        RoleConstants.SUPER_ADMIN.value,
        RoleConstants.FACILITY_REP.value,
    },
}

# # ----------------------------- Role Permission Mapper -----------------------------
ALL_PERMISSIONS = {p.value for p in PermissionConstants}

# # Minimal default permissions
DEFAULT_USER_PERMISSIONS = {
    PermissionConstants.VIEW_USER.value,
    PermissionConstants.CHANGE_USER_PASSWORD.value,
    PermissionConstants.LOGOUT_USER.value,
    PermissionConstants.CREATE_APPLICATION.value,
    PermissionConstants.VIEW_APPLICATION.value,
    PermissionConstants.LIST_APPLICATIONS.value,
}

# Admin specific permissions
ADMIN_PERMISSIONS = ALL_PERMISSIONS

# Facility Representative specific permissions
FACILITY_REP_PERMISSIONS = DEFAULT_USER_PERMISSIONS

# # Role_permissions mapping
ROLE_PERMISSION_MAPPER = {
    RoleConstants.SUPER_ADMIN.value: ALL_PERMISSIONS,
    RoleConstants.ADMIN.value: ADMIN_PERMISSIONS,
    RoleConstants.FACILITY_REP.value: FACILITY_REP_PERMISSIONS,
}

# # --------------------------- Application Permission Mapper ---------------------------
# # Map application identifiers (same keys as INTERNAL_APPLICATION_ALLOWED_ROLES) to permission sets.
APPLICATION_PERMISSION_MAPPER = {
    "health-facilities-tracker-web": ALL_PERMISSIONS,
}
