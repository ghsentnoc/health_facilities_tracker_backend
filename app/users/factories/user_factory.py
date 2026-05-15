from sqlalchemy.orm import Session

from app.auth.config.auth_config import auth_config
from app.auth.dependencies.role_service_dependency import create_role_service
from app.auth.services.token_service import TokenService
from app.auth.utils.hash_password import PasswordHashManager
from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.core.services.notification_publisher_service import NotificationPublisherService
from app.locations.dependencies.facility_service_dependency import create_facility_service
from app.users.dependencies.user_facility_association_service_dependency import create_user_facility_association_service
from app.users.dependencies.user_profile_service_dependency import create_user_profile_service
from app.users.models import User
from app.users.repositories.user_repository import UserRepository
from app.users.services.user_service import UserService


class UserRepositoryFactory(BaseRepositoryFactory[User, UserRepository]):
    """A factory for creating user repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> UserRepository:
        """Create a new user repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            UserRepository: The created user repository.
        """
        return cls._default_create(db_session=db_session, model=User, repository_class=UserRepository)


class UserServiceFactory:
    """A factory for creating user services."""

    @classmethod
    def create(cls, *, user_repository: UserRepository) -> UserService:
        """Create a new user service.

        Args:
            user_repository (UserRepository): The user repository for data.

        Returns:
            UserService: The created user service.
        """
        facility_service = create_facility_service(db_session=user_repository.db_session)
        role_service = create_role_service(db_session=user_repository.db_session)
        user_profile_service = create_user_profile_service(db_session=user_repository.db_session)
        user_facility_association_service = create_user_facility_association_service(
            db_session=user_repository.db_session
        )
        password_hash_manager = PasswordHashManager()
        token_service = TokenService(secret=auth_config.JWT_SECRET_KEY, algorithm=auth_config.JWT_ALGORITHM)
        notification_publisher = NotificationPublisherService()
        return UserService(
            user_repository=user_repository,
            user_profile_service=user_profile_service,
            facility_service=facility_service,
            role_service=role_service,
            password_hash_manager=password_hash_manager,
            token_service=token_service,
            notification_publisher=notification_publisher,
            user_facility_association_service=user_facility_association_service,
        )
