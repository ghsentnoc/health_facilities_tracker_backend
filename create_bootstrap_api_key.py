"""Bootstrap script: creates an active application + API key for testing."""
import sys

from dotenv import load_dotenv

load_dotenv()

from app.auth.factories.api_keys_factory import APIKeyRepositoryFactory, APIKeyServiceFactory
from app.auth.factories.application_factory import ApplicationRepositoryFactory, ApplicationServiceFactory
from app.auth.schemas.request.applications_api_key import CreateApplicationRequestSchema
from app.database.session import SessionLocal
from app.users.repositories.user_repository import UserRepository
from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.users.models import User

APP_NAME = "bootstrap-test-app"

db = SessionLocal()

try:
    # Resolve the super admin user
    user = db.query(User).filter_by(is_deleted=False).order_by(User.created_at).first()
    if not user:
        print("ERROR: No users found. Run create_super_admin.py first.")
        sys.exit(1)

    print(f"Using user: {user.email} (id={user.id})")

    # Check if the bootstrap app already exists
    from app.auth.models.applications_api_key import Application
    existing_app = db.query(Application).filter_by(app_name=APP_NAME, is_deleted=False).first()
    if existing_app and existing_app.is_active:
        print(f"Bootstrap app already exists and is active: {existing_app.id}")
        print("Rotating key to get a fresh plaintext key...")
        api_key_repo = APIKeyRepositoryFactory.create(db_session=db)
        api_key_service = APIKeyServiceFactory.create(api_key_repository=api_key_repo)
        plain_text = api_key_service.rotate_api_key(
            application_id=str(existing_app.id), current_user=user
        )
        print(f"\nAPI_KEY={plain_text}\n")
        print("Copy this key — it will only be shown once.")
        sys.exit(0)

    # Build services
    api_key_repo = APIKeyRepositoryFactory.create(db_session=db)
    api_key_service = APIKeyServiceFactory.create(api_key_repository=api_key_repo)
    app_repo = ApplicationRepositoryFactory.create(db_session=db)
    from app.auth.utils.hash_password import PasswordHashManager
    app_service = ApplicationServiceFactory.create(
        application_repository=app_repo, api_key_service=api_key_service, hash_manager=PasswordHashManager()
    )

    # Create the application (inactive by default)
    app_data = CreateApplicationRequestSchema(app_name=APP_NAME, platform="web")
    application, plain_text = app_service.create(current_user=user, application_data=app_data)
    print(f"Application created: {application.id}")

    # Activate the application (generates a new valid API key)
    application, plain_text = app_service.activate_application(application_id=str(application.id))
    print(f"Application activated.")
    print(f"\nAPI_KEY={plain_text}\n")
    print("Copy this key — it will only be shown once.")

finally:
    db.close()
