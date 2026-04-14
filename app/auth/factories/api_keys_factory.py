from sqlalchemy.orm import Session

from app.auth.models import APIKey
from app.auth.repositories.applications__api_key_repository import APIKeyRepository
from app.auth.services.applications__api_key_service import APIKeyService
from app.auth.utils.hash_password import PasswordHashManager
from app.core.factories.base_repository_factory import BaseRepositoryFactory


class APIKeyRepositoryFactory(BaseRepositoryFactory[object, APIKeyRepository]):
    """A factory for creating APIKey repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> APIKeyRepository:
        """Create a new APIKey repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            APIKeyRepository: The created APIKey repository.
        """
        return cls._default_create(db_session=db_session, model=APIKey, repository_class=APIKeyRepository)


class APIKeyServiceFactory:
    """A factory for creating APIKey services."""

    @classmethod
    def create(cls, *, api_key_repository: APIKeyRepository) -> APIKeyService:
        """Create a new APIKey service.

        Args:
            api_key_repository (APIKeyRepository): The api key repository for data.

        Returns:
            APIKeyService: The created api key service.
        """
        hash_manager = PasswordHashManager()
        return APIKeyService(api_key_repository=api_key_repository, hash_manager=hash_manager)
