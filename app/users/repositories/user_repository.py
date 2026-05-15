from typing import Any, Literal, Optional, Type, Union

from sqlalchemy.orm import Session, joinedload

from app.auth.models import Role
from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.locations.models import Facility
from app.users.models import User, UserProfile


class UserRepository(BaseReadRepository[User], BaseWriteRepository[User]):
    """Repository for managing User entities."""

    def __init__(self, *, db_session: Session, model: type[User] = User) -> None:
        """Initialize the UserRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The User model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, data: dict) -> User:  # type: ignore
        """Create a new User entity.

        Args:
            data (dict): The data needed to create the user

        Returns:
            User: The created user.
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
    ) -> Union[list[User], list[Type[User]]]:
        """Retrieve all users.

        Args:
            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[User]: A list of all entity instances.
        """
        query = self.db_session.query(User)
        query = query.options(joinedload(User.profile), joinedload(User.roles), joinedload(User.user_facility))

        if filters:
            if filters.get("first_name") or filters.get("phone_number") or filters.get("country"):
                query = query.join(UserProfile)

            if filters.get("first_name"):
                filters["first_name"].update({"field_name": "first_name", "model": UserProfile})

            if filters.get("phone_number"):
                filters["phone_number"].update({"field_name": "phone_number", "model": UserProfile})

            if filters.get("country"):
                filters["country"].update({"field_name": "country", "model": UserProfile})

            if filters.get("facility_name"):
                query = query.join(User.user_facility)
                filters["facility_name"].update({"field_name": "name", "model": Facility})

            if filters.get("role"):
                query = query.join(Role)
                filters["role"].update({"field_name": "name", "model": Role})

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )

    def approve_user(self, *, user_id: str) -> User | None:
        """Approve a user.

        Args:
            user_id (str): The ID of the user to approve.

        Returns:
            User: The approved user.
        """
        user = self.get_by_id(entity_id=user_id)

        if user:
            user.is_approved = True  # type: ignore
            return self.save(object_to_save=user)

        return user

    def update(self, *, entity: User, update_data: dict) -> User:
        """Update a user."""
        raise NotImplementedError

    def get_by_auth_identifier(self, *, identifier_type: Literal["email", "phone_number"], value: str) -> User | None:
        """Get a user by the credential used during authentication."""
        query = self.db_session.query(User)
        query = query.options(joinedload(User.profile), joinedload(User.roles), joinedload(User.user_facility))

        if identifier_type == "phone_number":
            query = query.join(UserProfile).filter(UserProfile.phone_number == value)
        else:
            query = query.filter(User.email == value)

        return query.first()
