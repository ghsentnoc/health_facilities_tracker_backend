from typing import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies.auth_dependency import get_current_user, validate_api_key
from app.auth.models import Application
from app.core.utils.messages import ErrorMessages
from app.users.models import User


def user_permissions_required(*, required_permissions: list[str]) -> Callable:
    """Dependency to check if the user has the required permissions.

    Args:
        required_permissions (list[str]): List of required permission strings.

    Returns:
        Callable: A FastAPI dependency function.
    """

    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> None:
        if not current_user.active_role:
            print(current_user.active_role)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ErrorMessages.UNAUTHORIZED_USER.value,
            )
        user_permission_check(required_permissions=required_permissions, current_user=current_user)

    return dependency


def application_permissions_required(*, required_permissions: list[str]) -> Callable:
    """Dependency to check if the user has the required permissions.

    Args:
        required_permissions (list[str]): List of required permission strings.

    Returns:
        Callable: A FastAPI dependency function.
    """

    def dependency(application: Application = Depends(validate_api_key)) -> None:
        application_permission_check(required_permissions=required_permissions, application=application)

    return dependency


def application_permission_check(*, required_permissions: list[str], application: Application) -> None:
    """Check if the application has the required permissions.

    Args:
        required_permissions (list[str]): List of required permission strings.
        application (Application): The application instance
    """
    application_permissions = {perm.name for perm in application.permissions}

    if not set(required_permissions).intersection(application_permissions):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorMessages.UNAUTHORIZED_APP.value)


def user_permission_check(*, required_permissions: list[str], current_user: User) -> None:
    """Check if the user has the required permissions.

    Args:
        required_permissions (list[str]): List of required permission strings.
        current_user (User): The current user instance.
    """
    if not current_user.active_role:
        print(current_user.active_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessages.UNAUTHORIZED_USER.value,
        )
    user_permissions = {perm.name for perm in current_user.active_role.permissions}
    print("user_permissions: ", user_permissions)
    if not user_permissions.intersection(set(required_permissions)):
        print(current_user.active_role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessages.UNAUTHORIZED_USER.value,
        )
