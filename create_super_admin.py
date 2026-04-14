from pydantic import BaseModel

from app.auth.factories.role_factory import RoleRepositoryFactory
from app.auth.utils.constants import RoleConstants
from app.auth.utils.hash_password import PasswordHashManager
from app.core.dependencies.database_dependency import db_session_dependency
from app.core.utils.validators import is_valid_password
from app.users.factories.user_factory import UserRepositoryFactory
from app.users.factories.user_profile_factory import UserProfileRepositoryFactory
from app.users.models import User, UserProfile


class SuperAdminSchema(BaseModel):
    """Schema to create a super administrator."""

    email: str
    password: str
    phone_number: str
    first_name: str
    last_name: str
    country: str


def create_super_admin(user_details: SuperAdminSchema) -> None:
    """Create a super administrator.

    Args:
        user_details (SuperAdminSchema): The details of the super administrator
    """
    if not is_valid_password(password=user_details.password):
        raise ValueError("Invalid password.")

    db_session_generator = db_session_dependency()
    db_session = next(db_session_generator)  # type: ignore

    role_repository = RoleRepositoryFactory.create(db_session=db_session)
    user_repository = UserRepositoryFactory.create(db_session=db_session)
    user_profile_repository = UserProfileRepositoryFactory.create(db_session=db_session)
    password_hash_service = PasswordHashManager()

    try:
        super_admin_role = role_repository.get_by_field(
            field_name="name", value=RoleConstants.SUPER_ADMIN.value, operator="eq"
        )

        new_user = User(
            email=user_details.email,  # type: ignore
            password_hash=password_hash_service.hash_password(password=user_details.password),  # type: ignore
            is_verified=True,  # type: ignore
        )

        saved_user = user_repository.save(object_to_save=new_user)
        saved_user.roles = [super_admin_role]

        user_profile = UserProfile(
            user_id=saved_user.id,  # type: ignore
            first_name=user_details.first_name,  # type: ignore
            phone_number=user_details.phone_number,  # type: ignore
            last_name=user_details.last_name,  # type: ignore
            country=user_details.country,  # type: ignore
        )

        user_profile_repository.save(object_to_save=user_profile)

        user_repository.save(object_to_save=saved_user)

    except Exception as e:
        print(str(e))

    finally:
        db_session.commit()
        db_session.close()
        db_session_generator.close()

    print("Super administrator created successfully.")


if __name__ == "__main__":
    _user_details = SuperAdminSchema(
        email="super_admin@ghs.gov.gh",
        password="Password123",
        phone_number="(233)111111111",
        first_name="Super",
        last_name="Administrator",
        country="Ghana",
    )

    create_super_admin(user_details=_user_details)
