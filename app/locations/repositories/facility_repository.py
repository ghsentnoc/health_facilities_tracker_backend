from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session, joinedload

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.core.schemas.query_params_schemas import JoinedSortSchema
from app.locations.models import District, Facility, Region


class FacilityRepository(BaseReadRepository[Facility], BaseWriteRepository[Facility]):
    """Repository for managing Facility entities."""

    def __init__(self, *, db_session: Session, model: type[Facility] = Facility) -> None:
        """Initialize the FacilityRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The Facility model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> Facility:
        """The method to create a new facility entity.

        Args:
            data (dict): The facility data needed to create the entity.

        Returns:
            Facility: The newly created facility.
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
    ) -> Union[list[Facility], list[Type[Facility]]]:
        """Get all entities.

        Args:
            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Facility]: A list of all entity instances.
        """
        joined_sort = []

        query = self.db_session.query(Facility)
        query = query.options(joinedload(Facility.district).joinedload(District.region))

        if filters:
            if filters.get("region_name") or filters.get("region_id"):
                query = query.join(Facility.district).join(District.region)

            if filters.get("region_name"):
                filters["region_name"].update({"field_name": "name", "model": Region})

            if filters.get("region_id"):
                filters["region_id"].update({"field_name": "id", "model": Region})

            if filters.get("district_name"):
                query = query.join(Facility.district)
                filters["district_name"].update({"field_name": "name", "model": District})

        if sort.get("region_name"):  # type: ignore
            joined_sort.append(JoinedSortSchema(field="name", model="region", direction=sort.get("region_name")))  # type: ignore

        if sort.get("district_name"):  # type: ignore
            joined_sort.append(JoinedSortSchema(field="name", model="district", direction=sort.get("district_name")))  # type: ignore

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )

    def approve_facility(self, *, facility_id: str) -> Facility | None:
        """Approve a facility.

        Args:
            facility_id (str): The id of the facility to approve.

        Returns:
            Facility: The approved facility.
        """
        facility = self.get_by_id(entity_id=facility_id)

        if facility:
            facility.is_approved = True  # type: ignore
            return self.save(object_to_save=facility)
        return facility

    def license_facility(self, *, facility_id: str) -> Facility | None:
        """License a facility.

        Args:
            facility_id (str): The id of the facility to license.

        Returns:
            Facility: The licensed facility.
        """
        facility = self.get_by_id(entity_id=facility_id)

        if facility:
            facility.is_licensed = True  # type: ignore
            return self.save(object_to_save=facility)
        return facility
