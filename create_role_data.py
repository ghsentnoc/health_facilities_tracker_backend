from app.auth.factories.role_factory import RoleRepositoryFactory
from app.auth.schemas.request.role import CreateRoleSchema
from app.auth.utils.constants import RoleConstants
from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.dependencies.database_dependency import db_session_dependency


def create_role_data() -> None:
    """Create default roles data."""
    db_session_generator = db_session_dependency()
    db_session = next(db_session_generator)  # type: ignore

    try:
        role_repository = RoleRepositoryFactory.create(db_session=db_session)

        print("-------------------------CREATING SYSTEM ROLES-------------------------")

        for role in RoleConstants:
            try:
                role_obj = role_repository.create(data=CreateRoleSchema(name=role.value))
                print(f"Role {role_obj.name} created.")

            except ObjectAlreadyExistsException:
                print(f"Role already exists: {role.value}")

        print("DONE")

    finally:
        db_session.commit()
        db_session.close()
        db_session_generator.close()


if __name__ == "__main__":
    create_role_data()
