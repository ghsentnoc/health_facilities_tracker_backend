from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.factories.application_factory import ApplicationRepositoryFactory, ApplicationServiceFactory
from app.auth.services.applications__api_key_service import ApplicationService
from app.auth.utils.hash_password import PasswordHashManager
from app.core.dependencies.database_dependency import db_session_dependency


def create_application_service(*, db_session: Session = Depends(db_session_dependency)) -> ApplicationService:
    """Dependency to create a new ApplicationService.

    The ApplicationService depends on the APIKeyService and a PasswordHashManager.

    Args:
        db_session (Session): The database session for the repositories and services.

    Returns:
        ApplicationService: The created application service.
    """
    from app.auth.dependencies.api_keys_dependency import create_api_key_service

    application_repository = ApplicationRepositoryFactory.create(db_session=db_session)
    api_key_service = create_api_key_service(db_session=application_repository.db_session)
    hash_manager = PasswordHashManager()

    return ApplicationServiceFactory.create(
        application_repository=application_repository, api_key_service=api_key_service, hash_manager=hash_manager
    )
