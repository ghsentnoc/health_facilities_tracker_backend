from app.auth.config.auth_config import auth_config
from app.auth.dependencies.auth_session_service_dependency import create_auth_session_service
from app.auth.dependencies.refresh_token_service_dependency import create_refresh_token_service
from app.auth.dependencies.role_service_dependency import create_role_service
from app.auth.services.auth_service import AuthService
from app.auth.services.token_service import TokenService
from app.auth.utils.hash_password import PasswordHashManager
from app.core.services.mail_service import MailServiceBuilder
from app.users.dependencies.user_service_dependency import create_user_service
from app.users.repositories.user_repository import UserRepository


class AuthServiceFactory:
    """A factory for creating auth services."""

    @classmethod
    def create(cls, *, user_repository: UserRepository) -> AuthService:
        """Create a new auth service.

        Args:
            user_repository (UserRepository): The user repository for data.

        Returns:
            UserService: The created auth service.
        """
        role_service = create_role_service(db_session=user_repository.db_session)
        user_service = create_user_service(db_session=user_repository.db_session)
        password_hash_manager = PasswordHashManager()
        mail_service = MailServiceBuilder()
        token_service = TokenService(secret=auth_config.JWT_SECRET_KEY, algorithm=auth_config.JWT_ALGORITHM)
        refresh_token_service = create_refresh_token_service(db_session=user_repository.db_session)
        auth_session_service = create_auth_session_service(db_session=user_repository.db_session)

        return AuthService(
            user_repository=user_repository,
            user_service=user_service,
            role_service=role_service,
            refresh_token_service=refresh_token_service,
            password_hash_manager=password_hash_manager,
            mail_service=mail_service,
            token_service=token_service,
            auth_session_service=auth_session_service,
        )
