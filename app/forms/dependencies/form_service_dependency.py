from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies.database_dependency import db_session_dependency
from app.forms.factories.form_factory import FormRepositoryFactory, FormServiceFactory
from app.forms.services.form_service import FormService


def create_form_service(*, db_session: Session = Depends(db_session_dependency)) -> FormService:
    """Dependency to create a new form service.

    Args:
        db_session (Session): The database session needed for the form service.

    Returns:
        FormService: The created form service.
    """
    form_repository = FormRepositoryFactory.create(db_session=db_session)
    return FormServiceFactory.create(form_repository=form_repository)
