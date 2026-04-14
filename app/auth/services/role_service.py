from typing import Optional

from fastapi import HTTPException, status

from app.auth.models import Role
from app.auth.repositories.role_repository import RoleRepository
from app.auth.schemas.request.role import CreateRoleSchema, UpdateRoleSchema
from app.auth.utils.allowed_filters_sort import allowed_role_filters, allowed_role_sorts, role_filters_without_joins
from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService


class RoleService(BaseService[Role]):
    """The service class for 'role'."""

    def __init__(self, *, role_repository: RoleRepository) -> None:
        """Initializer for 'role' service.

        Args:
            role_repository (RoleRepository): The role repository.
        """
        self.role_repository = role_repository
        super().__init__(main_repository=role_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[Role]:
        """Get all role entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Role]: A list of all entity instances
        """
        return self._default_get_all(
            filters_without_joins=role_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_role_filters,
            allowed_sorts=allowed_role_sorts,
        )

    def create(self, *, role_data: CreateRoleSchema) -> Role:
        """Create a new role.

        Args:
            role_data (CreateRoleSchema): The role data to create.

        Returns:
            Role: The newly created role.
        """
        return self._default_create(
            entity_schema=role_data, unique_field_to_check="name", unique_field_value=role_data.name
        )

    def update(self, *, role_id: str, data_to_update: UpdateRoleSchema) -> Role:
        """Update a role.

        Args:
            role_id (str): The id of the role to update.
            data_to_update: The data to update the role with.

        Returns:
            Role: The updated role.
        """
        role = self.get_by_id(entity_id=role_id)

        try:
            updated_role = self.role_repository.update(entity=role, update_data=data_to_update.model_dump())
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return updated_role
