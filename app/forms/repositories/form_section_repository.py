from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session, joinedload

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.forms.models import FormSection


class FormSectionRepository(BaseReadRepository[FormSection], BaseWriteRepository[FormSection]):
    """Repository for managing FormSection entities."""

    def __init__(self, *, db_session: Session, model: type[FormSection] = FormSection) -> None:
        """Initialize the FormSectionRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (FormSection): The FormSection model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> FormSection:
        """Create a new form section entity.

        Args:
            data (dict): The form section data needed to create the entity.

        Returns:
            FormSection: The newly created form section.
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
    ) -> Union[list[FormSection], list[Type[FormSection]]]:
        """Get all form section entities.

        Args:
            filters_without_joins (list): Filters without joins.
            filters_with_joins (list): Filters with joins.
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[FormSection]: A list of all form section instances.
        """
        query = self.db_session.query(FormSection)
        query = query.options(joinedload(FormSection.fields))

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )

    def get_sections_for_form(self, *, form_id: str) -> list[FormSection]:
        """Get all sections belonging to a specific form.

        Args:
            form_id (str): The ID of the form.

        Returns:
            list[FormSection]: A list of form sections for the form.
        """
        return (
            self.db_session.query(FormSection)
            .options(joinedload(FormSection.fields))
            .filter_by(form_id=form_id, is_deleted=False)
            .order_by(FormSection.order)
            .all()
        )
