from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session, joinedload

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.forms.models import Form, FormField, FormSection


class FormRepository(BaseReadRepository[Form], BaseWriteRepository[Form]):
    """Repository for managing Form entities."""

    def __init__(self, *, db_session: Session, model: type[Form] = Form) -> None:
        """Initialize the FormRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (Form): The Form model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> Form:
        """Create a new form entity.

        Args:
            data (dict): The form data needed to create the entity.

        Returns:
            Form: The newly created form.
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
    ) -> Union[list[Form], list[Type[Form]]]:
        """Get all form entities.

        Args:
            filters_without_joins (list): Filters without joins.
            filters_with_joins (list): Filters with joins.
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[Form]: A list of all form instances.
        """
        query = self.db_session.query(Form)
        query = query.options(
            joinedload(Form.sections).joinedload(FormSection.fields)
        )

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )

    def get_by_id(self, *, entity_id: str) -> Optional[Form]:
        """Get a form by its ID with sections and fields eagerly loaded.

        Args:
            entity_id (str): The ID of the form.

        Returns:
            Optional[Form]: The form instance.
        """
        return (
            self.db_session.query(Form)
            .options(joinedload(Form.sections).joinedload(FormSection.fields))
            .filter_by(id=entity_id)
            .first()
        )
