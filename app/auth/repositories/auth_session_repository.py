from typing import Any, Optional, Type, Union

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.auth.models import AuthSession
from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository


class AuthSessionRepository(BaseReadRepository[AuthSession], BaseWriteRepository[AuthSession]):
    """Repository for managing AuthSession entities."""

    def get_all(
        self,
        *,
        filters_without_joins: list,
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
        jurisdiction_zone: Optional[list[str]] = None,
    ) -> Union[list[AuthSession], list[Type[AuthSession]]]:
        """Get all auth_sessions.

            filters_without_joins (list): Filters without no joins
            filters_with_joins (list): Filters with joins
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.
            jurisdiction_zone (list[str], optional): Jurisdiction zone filter.

        Returns:
            list[AuthSession]: A list of all entity instances.
        """
        raise NotImplementedError

    def __init__(self, *, db_session: Session, model: type[AuthSession] = AuthSession) -> None:
        """Initialize the AuthSessionRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (User): The AuthSession model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> AuthSession:
        """The method to create a new auth_session entity.

        Args:
            data (dict): The auth_session data needed to create the entity.

        Returns:
            AuthSession: The newly created auth_session.
        """
        return self._default_create(data=data)

    def update(self, *, entity: AuthSession, update_data: dict) -> AuthSession:
        """The method to update a new auth_session entity.

        Args:
            entity (AuthSession): The auth session entity to update.
            update_data (dict): The auth_session data needed to create the entity.

        Returns:
            AuthSession: The newly updated auth_session.
        """
        raise NotImplementedError

    def get_session_by_device_id_user_id(
        self, *, device_id: str, user_id: str, client_type: str
    ) -> Optional[AuthSession]:
        """Get an active auth session by device ID.

        Args:
            device_id (str): The device ID to search for.
            user_id (str): The user ID to search for.
            client_type (str): The client type to search for.

        Returns:
            Optional[AuthSession]: The active auth session if found, else None.
        """
        return (
            self.db_session.query(AuthSession)
            .filter(
                and_(
                    AuthSession.device_id == device_id,  # type: ignore
                    AuthSession.user_id == user_id,  # type: ignore
                    AuthSession.client_type == client_type,  # type: ignore
                ),
                AuthSession.is_deleted.is_(False),
            )
            .first()
        )
