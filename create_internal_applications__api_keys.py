from app.auth.dependencies.application_dependency import create_application_service
from app.auth.schemas.request.applications_api_key import CreateApplicationRequestSchema
from app.auth.utils.constants import INTERNAL_APPLICATIONS
from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.dependencies.database_dependency import db_session_dependency
from app.users.dependencies.user_service_dependency import create_user_service


def create_applications_data() -> None:
    """Create default applications and API keys."""
    db_session_generator = db_session_dependency()
    db_session = next(db_session_generator)  # type: ignore

    try:
        application_service = create_application_service(db_session=db_session)
        user_service = create_user_service(db_session=db_session)

        user = user_service.get_by_field(field_name="email", value="super_admin@ghs.gov.gh", operator="eq")  # type: ignore

        print("-------------------------CREATING APPLICATIONS-------------------------")

        for application, platform in INTERNAL_APPLICATIONS.items():
            try:
                new_application, api_key = application_service.create(
                    current_user=user,  # type: ignore
                    application_data=CreateApplicationRequestSchema(
                        app_name=application,
                        platform=platform,  # type: ignore
                    ),
                )

                print(f"Application {new_application.to_dict()} created.")
                print(f"API KEY: {api_key}")
                print("PLEASE STORE THIS API KEY SECURELY. IT WILL NOT BE SHOWN AGAIN.")
                print("--------------------------------------------------------------------------")

            except ObjectAlreadyExistsException:
                print(f"Application already exists: {application}")

        print("DONE")

    finally:
        db_session.commit()
        db_session.close()
        db_session_generator.close()


if __name__ == "__main__":
    create_applications_data()
