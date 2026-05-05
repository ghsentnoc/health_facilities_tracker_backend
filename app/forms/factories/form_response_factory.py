from sqlalchemy.orm import Session

from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.forms.factories.form_factory import FormFieldRepositoryFactory, FormRepositoryFactory
from app.forms.models import FormResponse
from app.forms.repositories.form_response_repository import FormResponseRepository
from app.forms.services.form_response_service import FormResponseService


class FormResponseRepositoryFactory(BaseRepositoryFactory[FormResponse, FormResponseRepository]):
    """A factory for creating form response repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> FormResponseRepository:
        """Create a new form response repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            FormResponseRepository: The created form response repository.
        """
        return cls._default_create(db_session=db_session, model=FormResponse, repository_class=FormResponseRepository)


class FormResponseServiceFactory:
    """A factory for creating form response services."""

    @classmethod
    def create(cls, *, form_response_repository: FormResponseRepository) -> FormResponseService:
        """Create a new form response service.

        Args:
            form_response_repository (FormResponseRepository): The form response repository.

        Returns:
            FormResponseService: The created form response service.
        """
        form_repository = FormRepositoryFactory.create(db_session=form_response_repository.db_session)
        form_field_repository = FormFieldRepositoryFactory.create(db_session=form_response_repository.db_session)
        return FormResponseService(
            form_response_repository=form_response_repository,
            form_repository=form_repository,
            form_field_repository=form_field_repository,
        )
