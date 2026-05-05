from typing import Any, Optional, Type, Union

from sqlalchemy.orm import Session

from app.core.repositories.sql_base_repository import BaseReadRepository, BaseWriteRepository
from app.forms.models import FormResponse


class FormResponseRepository(BaseReadRepository[FormResponse], BaseWriteRepository[FormResponse]):
    """Repository for managing FormResponse entities."""

    def __init__(self, *, db_session: Session, model: type[FormResponse] = FormResponse) -> None:
        """Initialize the FormResponseRepository with a database session and model.

        Args:
            db_session (Session): The SQLAlchemy database session.
            model (FormResponse): The FormResponse model class.
        """
        self.db_session = db_session
        self.model = model
        super().__init__(db_session=db_session, model=model)

    def create(self, *, data: dict) -> FormResponse:
        """Create a new form response entity.

        Args:
            data (dict): The form response data needed to create the entity.

        Returns:
            FormResponse: The newly created form response.
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
    ) -> Union[list[FormResponse], list[Type[FormResponse]]]:
        """Get all form response entities.

        Args:
            filters_without_joins (list): Filters without joins.
            filters_with_joins (list): Filters with joins.
            pagination (dict[str, int]): Pagination parameters.
            filters (dict[str, Any]): Filter parameters.
            sort (dict[str, str]): Sort parameters.

        Returns:
            list[FormResponse]: A list of all form response instances.
        """
        query = self.db_session.query(FormResponse)

        return self._default_get_all(
            filters_without_joins=filters_without_joins,
            filters_with_joins=filters_with_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            query=query,
        )

    def get_responses_for_form(self, *, form_id: str) -> list[FormResponse]:
        """Get all responses for a specific form.

        Args:
            form_id (str): The ID of the form.

        Returns:
            list[FormResponse]: A list of form responses for the form.
        """
        return self.db_session.query(FormResponse).filter_by(form_id=form_id, is_deleted=False).all()
