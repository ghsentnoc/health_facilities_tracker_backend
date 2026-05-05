from sqlalchemy.orm import Session

from app.core.factories.base_repository_factory import BaseRepositoryFactory
from app.forms.models import Form, FormField, FormSection
from app.forms.repositories.form_field_repository import FormFieldRepository
from app.forms.repositories.form_repository import FormRepository
from app.forms.repositories.form_section_repository import FormSectionRepository
from app.forms.services.form_service import FormService


class FormRepositoryFactory(BaseRepositoryFactory[Form, FormRepository]):
    """A factory for creating form repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> FormRepository:
        """Create a new form repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            FormRepository: The created form repository.
        """
        return cls._default_create(db_session=db_session, model=Form, repository_class=FormRepository)


class FormSectionRepositoryFactory(BaseRepositoryFactory[FormSection, FormSectionRepository]):
    """A factory for creating form section repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> FormSectionRepository:
        """Create a new form section repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            FormSectionRepository: The created form section repository.
        """
        return cls._default_create(db_session=db_session, model=FormSection, repository_class=FormSectionRepository)


class FormFieldRepositoryFactory(BaseRepositoryFactory[FormField, FormFieldRepository]):
    """A factory for creating form field repositories."""

    @classmethod
    def create(cls, *, db_session: Session) -> FormFieldRepository:
        """Create a new form field repository.

        Args:
            db_session (Session): The database session for the repository.

        Returns:
            FormFieldRepository: The created form field repository.
        """
        return cls._default_create(db_session=db_session, model=FormField, repository_class=FormFieldRepository)


class FormServiceFactory:
    """A factory for creating form services."""

    @classmethod
    def create(cls, *, form_repository: FormRepository) -> FormService:
        """Create a new form service.

        Args:
            form_repository (FormRepository): The form repository.

        Returns:
            FormService: The created form service.
        """
        form_section_repository = FormSectionRepositoryFactory.create(db_session=form_repository.db_session)
        form_field_repository = FormFieldRepositoryFactory.create(db_session=form_repository.db_session)
        return FormService(
            form_repository=form_repository,
            form_section_repository=form_section_repository,
            form_field_repository=form_field_repository,
        )
