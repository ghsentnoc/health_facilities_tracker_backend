from sqlalchemy.orm import Session

from app.auth.models import AuthSession
from app.auth.repositories.auth_session_repository import AuthSessionRepository
from app.auth.services.auth_session_service import AuthSessionService
from app.core.factories.base_repository_factory import BaseRepositoryFactory


class AuthSessionRepositoryFactory(BaseRepositoryFactory[AuthSession, AuthSessionRepository]):
    """A factory for creating auth session repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> AuthSessionRepository:
        """Create a new auth session repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            AuthSessionRepository: The created auth session repository.
        """
        return cls._default_create(db_session=db_session, model=AuthSession, repository_class=AuthSessionRepository)


class AuthSessionServiceFactory:
    """A factory for creating auth session services."""

    @classmethod
    def create(cls, *, auth_session_repository: AuthSessionRepository) -> AuthSessionService:
        """Create a new auth session service.

        Args:
            auth_session_repository (AuthSessionRepository): The auth session repository for data.

        Returns:
            AuthSessionService: The created auth session service.
        """
        return AuthSessionService(auth_session_repository=auth_session_repository)
