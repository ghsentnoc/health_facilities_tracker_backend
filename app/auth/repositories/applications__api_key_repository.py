from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session, joinedload

from app.auth.models import APIKey, Application
from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository


class ApplicationRepository(BaseReadRepository[Application], BaseWriteRepository[Application]):
    """Repository for managing Application entities."""

    def get_all(
        self,
        *,
        filters_without_joins: list,
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
        jurisdiction_zone: Optional[list[str]] = None,
    ) -> Union[list[Application], list[Type[Application]]]:
        """Get all regions.

            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.
            jurisdiction_zone (list[str], optional): Jurisdiction zone filter.

        Returns:
            list[Application]: A list of all entity instances.
        """
        query = self.db_session.query(Application)

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            filters=filters,
            sort=sort,
            pagination=pagination,
            query=query,
        )

    def __init__(self, *, db_session: Session, model: type[Application] = Application) -> None:
        """Initialize the ApplicationRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The Application model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> Application:
        """The method to create a new application entity.

        Args:
            data (dict): The application data needed to create the entity.

        Returns:
            T: The newly created application.
        """
        return self._default_create(data=data)


class APIKeyRepository(BaseReadRepository[APIKey], BaseWriteRepository[APIKey]):
    """Repository for managing APIKey entities."""

    def get_all(
        self,
        *,
        filters_without_joins: list,
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
        jurisdiction_zone: Optional[list[str]] = None,
    ) -> Union[list[APIKey], list[Type[APIKey]]]:
        """Get all regions.

            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.
            jurisdiction_zone (list[str], optional): Jurisdiction zone filter.

        Returns:
            list[APIKey]: A list of all entity instances.
        """
        query = self.db_session.query(APIKey)
        query = query.options(joinedload(APIKey.application))

        if filters and filters.get("app_name"):
            query = query.join(Application)
            filters["app_name"].update({"field_name": "app_name", "model": Application})

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            filters=filters,
            sort=sort,
            pagination=pagination,
            query=query,
        )

    def __init__(self, *, db_session: Session, model: type[APIKey] = APIKey) -> None:
        """Initialize the APIKeyRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The APIKey model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> APIKey:
        """The method to create a new application entity.

        Args:
            data (dict): The application data needed to create the entity.

        Returns:
            T: The newly created application.
        """
        return self._default_create(data=data)
