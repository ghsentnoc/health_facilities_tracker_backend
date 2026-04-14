from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.factories.auth_session_factory import AuthSessionRepositoryFactory, AuthSessionServiceFactory
from app.auth.services.auth_session_service import AuthSessionService
from app.core.dependencies.database_dependency import db_session_dependency


def create_auth_session_service(*, db_session: Session = Depends(db_session_dependency)) -> AuthSessionService:
    """Dependency to create a new auth session service.

    Args:
        db_session (Session): The database session needed for the auth session service.

    Returns:
        AuthSessionService: The created auth session service.
    """
    auth_session_repository = AuthSessionRepositoryFactory.create(db_session=db_session)
    return AuthSessionServiceFactory.create(auth_session_repository=auth_session_repository)
