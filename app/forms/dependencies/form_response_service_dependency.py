from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies.database_dependency import db_session_dependency
from app.forms.factories.form_response_factory import FormResponseRepositoryFactory, FormResponseServiceFactory
from app.forms.services.form_response_service import FormResponseService


def create_form_response_service(*, db_session: Session = Depends(db_session_dependency)) -> FormResponseService:
    """Dependency to create a new form response service.

    Args:
        db_session (Session): The database session needed for the form response service.

    Returns:
        FormResponseService: The created form response service.
    """
    form_response_repository = FormResponseRepositoryFactory.create(db_session=db_session)
    return FormResponseServiceFactory.create(form_response_repository=form_response_repository)
