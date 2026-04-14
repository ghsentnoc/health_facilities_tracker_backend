from typing import Any, Optional

from app.auth.models import Permission
from app.auth.repositories.permission_repository import PermissionRepository
from app.auth.schemas.request.permission import CreatePermissionSchema
from app.auth.utils.allowed_filters_sort import (
    allowed_permission_filters,
    allowed_permission_sorts,
    permission_filters_without_joins,
)
from app.core.services.base_service import BaseService


class PermissionService(BaseService[Permission]):
    """The service class for 'permission'."""

    def __init__(self, *, permission_repository: PermissionRepository) -> None:
        """Initializer for 'permission' service.

        Args:
            permission_repository (PermissionRepository): The permission repository.
        """
        self.permission_repository = permission_repository
        super().__init__(main_repository=permission_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[Permission]:
        """Get all permission entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Permission]: A list of all entity instances
        """
        return self._default_get_all(
            filters_without_joins=permission_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_permission_filters,
            allowed_sorts=allowed_permission_sorts,
        )

    def create(self, *, permission_data: CreatePermissionSchema) -> Permission:
        """Create a new permission.

        Args:
            permission_data (CreatePermissionSchema): The permission data to create.

        Returns:
            Permission: The newly created permission.
        """
        return self._default_create(
            entity_schema=permission_data, unique_field_to_check="name", unique_field_value=permission_data.name
        )

    def update(self, *args, **kwargs) -> Any:  # type: ignore
        """Update a permission."""
        return NotImplemented
