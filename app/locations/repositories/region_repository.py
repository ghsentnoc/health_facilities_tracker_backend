from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.locations.models import Region


class RegionRepository(BaseReadRepository[Region], BaseWriteRepository[Region]):
    """Repository for managing Region entities."""

    def __init__(self, *, db_session: Session, model: type[Region] = Region) -> None:
        """Initialize the RegionRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The Region model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> Region:
        """The method to create a new region entity.

        Args:
            data (dict): The region data needed to create the entity.

        Returns:
            Region: The newly created region.
        """
        return self._default_create(data=data)

    def get_all(
        self,
        *,
        filters_without_joins: list[str],
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[Region], list[Type[Region]]]:
        """Get all regions.

            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Region]: A list of all entity instances.
        """
        query = self.db_session.query(Region)

        return self._default_get_all(
            filters_without_joins=filters_without_joins, filters=filters, sort=sort, pagination=pagination, query=query
        )
