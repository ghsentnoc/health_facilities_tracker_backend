from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.forms.models import FormField


class FormFieldRepository(BaseReadRepository[FormField], BaseWriteRepository[FormField]):
    """Repository for managing FormField entities."""

    def __init__(self, *, db_session: Session, model: type[FormField] = FormField) -> None:
        """Initialize the FormFieldRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (FormField): The FormField model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> FormField:
        """Create a new form field entity.

        Args:
            data (dict): The form field data needed to create the entity.

        Returns:
            FormField: The newly created form field.
        """
        return self._default_create(data=data)

    def get_all(
        self,
        *,
        filters_without_joins: list[str],
        filters_with_joins: Optional[list] = None,
        pagination: Optional[dict[str, int]] = None,
        filters: Optional[dict[str, Any]] = None,
        sort: Optional[dict[str, str]] = None,
    ) -> Union[list[FormField], list[Type[FormField]]]:
        """Get all form field entities.

        Args:
            filters_without_joins (list): Filters without joins.
            filters_with_joins (list): Filters with joins.
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[FormField]: A list of all form field instances.
        """
        query = self.db_session.query(FormField)

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )

    def get_fields_for_section(self, *, section_id: str) -> list[FormField]:
        """Get all fields belonging to a specific section.

        Args:
            section_id (str): The ID of the section.

        Returns:
            list[FormField]: A list of form fields for the section.
        """
        return (
            self.db_session.query(FormField)
            .filter_by(section_id=section_id, is_deleted=False)
            .order_by(FormField.order)
            .all()
        )

    def get_fields_for_form(self, *, form_id: str) -> list[FormField]:
        """Get all fields belonging to a specific form.

        Args:
            form_id (str): The ID of the form.

        Returns:
            list[FormField]: A list of form fields for the form.
        """
        return (
            self.db_session.query(FormField)
            .filter_by(form_id=form_id, is_deleted=False)
            .order_by(FormField.order)
            .all()
        )
