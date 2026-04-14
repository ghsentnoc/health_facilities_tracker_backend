from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.auth.models import Permission
from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository


class PermissionRepository(BaseReadRepository[Permission], BaseWriteRepository[Permission]):
    """Repository for managing Permission entities."""

    def get_all(
        self,
        *,
        filters_without_joins: list,
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[Permission], list[Type[Permission]]]:
        """Get all regions.

            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Region]: A list of all entity instances.
        """
        query = self.db_session.query(Permission)

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            filters=filters,
            sort=sort,
            pagination=pagination,
            query=query,
        )

    def __init__(self, *, db_session: Session, model: type[Permission] = Permission) -> None:
        """Initialize the PermissionRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The Permission model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, permission_data: dict) -> Permission:
        """The method to create a new permission entity.

        Args:
            permission_data (dict): The permission data needed to create the entity.

        Returns:
            T: The newly created permission.
        """
        return self._default_create(data=permission_data)
