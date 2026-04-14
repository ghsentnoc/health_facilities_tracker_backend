from sqlalchemy.orm import Session

from app.auth.models import Application
from app.auth.repositories.applications__api_key_repository import ApplicationRepository
from app.auth.services.applications__api_key_service import APIKeyService, ApplicationService
from app.auth.utils.hash_password import PasswordHashManager
from app.core.factories.base_repository_factory import BaseRepositoryFactory


class ApplicationRepositoryFactory(BaseRepositoryFactory[object, ApplicationRepository]):
    """A factory for creating Application repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> ApplicationRepository:
        """Create a new Application repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            ApplicationRepository: The created application repository.
        """
        return cls._default_create(db_session=db_session, model=Application, repository_class=ApplicationRepository)


class ApplicationServiceFactory:
    """A factory for creating Application services."""

    @classmethod
    def create(
        cls,
        *,
        application_repository: ApplicationRepository,
        api_key_service: APIKeyService,
        hash_manager: PasswordHashManager,
    ) -> ApplicationService:
        """Create a new Application service.

        Args:
            application_repository (ApplicationRepository): The application repository for data.
            api_key_service (APIKeyService): The api key service used by the application service.
            hash_manager (PasswordHashManager): The hash manager used to hash api keys.

        Returns:
            ApplicationService: The created application service.
        """
        return ApplicationService(
            application_repository=application_repository, api_key_service=api_key_service, hash_manager=hash_manager
        )
