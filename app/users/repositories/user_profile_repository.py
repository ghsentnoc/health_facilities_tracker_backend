from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.users.models import UserProfile


class UserProfileRepository(BaseReadRepository[UserProfile], BaseWriteRepository[UserProfile]):
    """Repository for managing UserProfile entities."""

    def __init__(self, *, db_session: Session, model: type[UserProfile] = UserProfile) -> None:
        """Initialize the UserProfileRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (UserProfile): The UserProfile model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, data: dict) -> UserProfile:  # type: ignore
        """Create a new UserProfile entity.

        Args:
            data (dict): The data needed to create the user profile.

        Returns:
            UserProfile: The created user profile.
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
    ) -> Union[list[UserProfile], list[Type[UserProfile]]]:
        """Retrieve all users.

        Args:
            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[UserProfile]: A list of all entity instances.
        """
        raise NotImplementedError
