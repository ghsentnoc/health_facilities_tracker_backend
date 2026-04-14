from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies.database_dependency import db_session_dependency
from app.users.factories.user_facility_association_factory import (
    UserFacilityAssociationRepositoryFactory,
    UserFacilityAssociationServiceFactory,
)
from app.users.services.user_facility_association_service import UserFacilityAssociationService


def create_user_facility_association_service(
    *, db_session: Session = Depends(db_session_dependency)
) -> UserFacilityAssociationService:
    """Dependency to create a new user facility association service.

    Args:
        db_session (Session): The database session needed for the user facility association service.

    Returns:
        UserService: The created user facility association service.
    """
    user_facility_association_repository = UserFacilityAssociationRepositoryFactory.create(db_session=db_session)
    return UserFacilityAssociationServiceFactory.create(
        user_facility_association_repository=user_facility_association_repository
    )
