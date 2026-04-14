from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session, joinedload

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.core.schemas.query_params_schemas import JoinedSortSchema
from app.locations.models import District, Region


class DistrictRepository(BaseReadRepository[District], BaseWriteRepository[District]):
    """Repository for managing District entities."""

    def __init__(self, *, db_session: Session, model: type[District] = District) -> None:
        """Initialize the DistrictRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The District model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> District:
        """The method to create a new district entity.

        Args:
            data (dict): The district data needed to create the entity.

        Returns:
            District: The newly created district.
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
    ) -> Union[list[District], list[Type[District]]]:
        """Get all entities.

        Args:
            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[District]: A list of all entity instances.
        """
        joined_sort = []

        query = self.db_session.query(District)
        query = query.options(joinedload(District.region))

        if filters and filters.get("region_name"):
            query = query.join(District.region)
            filters["region_name"].update({"field_name": "name", "model": Region})

        if sort.get("region_name"):  # type: ignore
            joined_sort.append(
                JoinedSortSchema(field="name", model="region", direction=sort.get("region_name"))  # type: ignore
            )

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )
