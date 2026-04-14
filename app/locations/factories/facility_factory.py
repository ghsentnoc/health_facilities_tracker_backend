from sqlalchemy.orm import Session

from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.locations.dependencies.district_service_dependency import create_district_service
from app.locations.factories.facility_contact_factory import FacilityContactRepositoryFactory
from app.locations.models import Facility
from app.locations.repositories.facility_repository import FacilityRepository
from app.locations.services.facility_service import FacilityService


class FacilityRepositoryFactory(BaseRepositoryFactory[Facility, FacilityRepository]):
    """A factory for creating facility repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> FacilityRepository:
        """Create a new facility repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            FacilityRepository: The created facility repository.
        """
        return cls._default_create(db_session=db_session, model=Facility, repository_class=FacilityRepository)


class FacilityServiceFactory:
    """A factory for creating facility services."""

    @classmethod
    def create(cls, *, facility_repository: FacilityRepository) -> FacilityService:
        """Create a new facility service.

        Args:
            facility_repository (FacilityRepository): The facility repository for data.

        Returns:
            FacilityService: The created facility service.
        """
        facility_contact_repository = FacilityContactRepositoryFactory.create(db_session=facility_repository.db_session)
        district_service = create_district_service(db_session=facility_repository.db_session)
        return FacilityService(
            facility_repository=facility_repository,
            facility_contact_repository=facility_contact_repository,
            district_service=district_service,
        )
