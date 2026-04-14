from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.auth.models import Permission, Role
from app.auth.schemas.request.role import CreateRoleSchema
from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository


class RoleRepository(BaseReadRepository[Role], BaseWriteRepository[Role]):
    """Repository for managing Role entities."""

    def get_all(
        self,
        *,
        filters_without_joins: list,
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[Role], list[Type[Role]]]:
        """Get all regions.

            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Region]: A list of all entity instances.
        """
        query = self.db_session.query(Role)

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            filters=filters,
            sort=sort,
            pagination=pagination,
            query=query,
        )

    def __init__(self, *, db_session: Session, model: type[Role] = Role) -> None:
        """Initialize the RoleRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The Role model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: CreateRoleSchema) -> Role:
        """The method to create a new role entity.

        Args:
            data (CreateRoleSchema): The role data needed to create the entity.

        Returns:
            T: The newly created role.
        """
        # create a new Role instance using the data
        new_role = Role(name=data.name)  # type: ignore

        # check if data has permission_ids query the permission tables for the ids and link it to the role.
        if data.permission_ids:
            permissions = self.db_session.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
            new_role.permissions = permissions

        # save the new role and return it.
        return self.save(object_to_save=new_role)

    def update(self, *, entity: Role, update_data: dict) -> Role:
        """Update a role with new data.

        Args:
            entity: The role to update.
            update_data: The data to update the role with.

        Returns:
            Role: The updated role.
        """
        if update_data["name"]:
            entity.name = update_data["name"]

        if update_data["permission_ids"]:
            permissions = (
                self.db_session.query(Permission).filter(Permission.id.in_(update_data["permission_ids"])).all()
            )
            entity.permissions = permissions

        return self.save(object_to_save=entity)
