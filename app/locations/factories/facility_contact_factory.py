from sqlalchemy.orm import Session

from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.locations.models import FacilityContact
from app.locations.repositories.facility_contact_repository import FacilityContactRepository


class FacilityContactRepositoryFactory(BaseRepositoryFactory[FacilityContact, FacilityContactRepository]):
    """A factory for creating facility contact repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> FacilityContactRepository:
        """Create a new facility contact repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            FacilityContactRepository: The created facility contact repository.
        """
        return cls._default_create(
            db_session=db_session, model=FacilityContact, repository_class=FacilityContactRepository
        )
