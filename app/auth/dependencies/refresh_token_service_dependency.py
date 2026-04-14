from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.factories.refresh_token_factory import RefreshTokenRepositoryFactory, RefreshTokenServiceFactory
from app.auth.services.refresh_token_service import RefreshTokenService
from app.core.dependencies.database_dependency import db_session_dependency


def create_refresh_token_service(*, db_session: Session = Depends(db_session_dependency)) -> RefreshTokenService:
    """Dependency to create a new refresh_token service.

    Args:
        db_session (Session): The database session needed for the refresh_token service.

    Returns:
        RefreshTokenService: The created refresh_token service.
    """
    refresh_token_repository = RefreshTokenRepositoryFactory.create(db_session=db_session)
    return RefreshTokenServiceFactory.create(refresh_token_repository=refresh_token_repository)
