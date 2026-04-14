from sqlalchemy.orm import Session

from app.auth.models import RefreshToken
from app.auth.repositories.refresh_token_repository import RefreshTokenRepository
from app.auth.services.refresh_token_service import RefreshTokenService
from app.core.factories.base_repository_factory import BaseRepositoryFactory


class RefreshTokenRepositoryFactory(BaseRepositoryFactory[RefreshToken, RefreshTokenRepository]):
    """A factory for creating refresh_token repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> RefreshTokenRepository:
        """Create a new refresh_token repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            RefreshTokenRepository: The created refresh_token repository.
        """
        return cls._default_create(db_session=db_session, model=RefreshToken, repository_class=RefreshTokenRepository)


class RefreshTokenServiceFactory:
    """A factory for creating refresh_token services."""

    @classmethod
    def create(cls, *, refresh_token_repository: RefreshTokenRepository) -> RefreshTokenService:
        """Create a new refresh_token service.

        Args:
            refresh_token_repository (RefreshTokenRepository): The refresh_token repository for data.

        Returns:
            RefreshTokenService: The created refresh_token service.
        """
        return RefreshTokenService(refresh_token_repository=refresh_token_repository)
