from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.factories.api_keys_factory import APIKeyRepositoryFactory, APIKeyServiceFactory
from app.auth.services.applications__api_key_service import APIKeyService
from app.core.dependencies.database_dependency import db_session_dependency


def create_api_key_service(*, db_session: Session = Depends(db_session_dependency)) -> APIKeyService:
    """Dependency to create a new APIKeyService.

    Args:
        db_session (Session): The database session for the repository and service.

    Returns:
        APIKeyService: The created API key service.
    """
    api_key_repository = APIKeyRepositoryFactory.create(db_session=db_session)
    return APIKeyServiceFactory.create(api_key_repository=api_key_repository)
