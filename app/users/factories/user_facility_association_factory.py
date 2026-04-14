from sqlalchemy.orm import Session

from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.users.models import UserFacilityAssociation
from app.users.repositories.user_facility_association_repository import UserFacilityAssociationRepository
from app.users.services.user_facility_association_service import UserFacilityAssociationService


class UserFacilityAssociationRepositoryFactory(
    BaseRepositoryFactory[UserFacilityAssociation, UserFacilityAssociationRepository]
):
    """A factory for creating user facility association repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> UserFacilityAssociationRepository:
        """Create a new user facility association repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            UserFacilityAssociationRepository: The created user facility association repository.
        """
        return cls._default_create(
            db_session=db_session, model=UserFacilityAssociation, repository_class=UserFacilityAssociationRepository
        )


class UserFacilityAssociationServiceFactory:
    """A factory for creating user facility association services."""

    @classmethod
    def create(
        cls, *, user_facility_association_repository: UserFacilityAssociationRepository
    ) -> UserFacilityAssociationService:
        """Create a new user facility association service.

        Args:
            user_facility_association_repository (UserFacilityAssociationRepository): \
                The user facility association repository for data.

        Returns:
            UserFacilityAssociationService: The created user facility association service.
        """
        return UserFacilityAssociationService(user_facility_association_repository=user_facility_association_repository)
