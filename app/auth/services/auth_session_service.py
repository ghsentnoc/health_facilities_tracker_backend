from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, status

from app.auth.models import AuthSession
from app.auth.repositories.auth_session_repository import AuthSessionRepository
from app.auth.schemas.request.auth_session import CreateAuthSessionSchema
from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService


class AuthSessionService(BaseService[AuthSession]):
    """The service class for 'auth_session'."""

    def __init__(self, *, auth_session_repository: AuthSessionRepository) -> None:
        """Initializer for 'auth_session' service.

        Args:
            auth_session_repository (AuthSessionRepository): The auth_session repository.
        """
        self.auth_session_repository = auth_session_repository
        super().__init__(main_repository=auth_session_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[AuthSession]:
        """Get all auth_session entities.

        Args:
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[AuthSession]: A list of all entity instances
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
        response = self.auth_session_repository.get_session_by_device_id_user_id(
            device_id=device_id,
            user_id=user_id,
            client_type=client_type,
        )

        if response is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auth session not found")
        return response

    def create(self, *, auth_session_data: CreateAuthSessionSchema) -> AuthSession:
        """Create a new auth_session.

        Args:
            auth_session_data (CreateAuthSessionSchema): The auth_session data to create.

        Returns:
            AuthSession: The newly created auth_session.
        """
        return self._default_create(entity_schema=auth_session_data)

    def revoke_auth_session_by_id(self, *, auth_session_id: str) -> AuthSession:
        """Revoke an auth session by its ID.

        Args:
            auth_session_id (str): The ID of the auth session to revoke.

        Returns:
            AuthSession: The revoked auth session.
        """
        # get the auth session by id.
        auth_session = self.get_by_id(entity_id=auth_session_id)

        # revoke the auth session and return it.
        return self.__revoke_auth_session(auth_session=auth_session)

    def revoke_auth_sessions_by_user_id(self, *, user_id: str) -> list[AuthSession]:
        """Revoke auth sessions by the user ID.

        Args:
            user_id (str): The ID of the user to revoke their auth sessions.

        Returns:
            list[AuthSession]: The list of auth sessions revoked.
        """
        # create a list to hold revoked auth sessions
        results = []

        # get all auth session by user id
        auth_sessions = self.auth_session_repository.get_by_field(  # type: ignore
            field_name="user_id", value=user_id, operator="eq"
        )

        # loop through user's auth sessions and revoke them
        if auth_sessions:
            for auth_session in auth_sessions:  # type: ignore
                results.append(self.__revoke_auth_session(auth_session=auth_session))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No auth sessions found for user")

        return results

    def update(self, *, entity: Any, update_data: Any) -> AuthSession:
        """The method to update a new auth_session entity.

        Args:
            entity (AuthSession): The auth session entity to update.
            update_data (dict): The auth_session data needed to create the entity.

        Returns:
            AuthSession: The newly updated auth_session.
        """
        raise NotImplementedError

    def __revoke_auth_session(self, auth_session: AuthSession) -> AuthSession:
        """Private method to revoke an auth session

        Args:
            auth_session (AuthSession): The auth session to revoke.

        Returns:
            AuthSession: The revoked auth session.
        """
        # revoke auth session
        auth_session.revoked_at = datetime.now(tz=timezone.utc)  # type: ignore
        auth_session.is_revoked = True  # type: ignore

        # save revoked auth session
        try:
            revoked_auth_session = self.auth_session_repository.save(object_to_save=auth_session)
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return revoked_auth_session
