from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.core.utils.messages import ErrorMessages
from app.forms.models import Form, FormField, FormResponse
from app.forms.repositories import FormFieldRepository, FormRepository, FormResponseRepository
from app.forms.schemas.request.form_response import CreateFormResponseRequestSchema
from app.forms.utils.allowed_filters_sort import (
    allowed_form_response_filters,
    allowed_form_response_sorts,
    form_response_filters_with_joins,
    form_response_filters_without_joins,
)


class FormResponseService(BaseService[FormResponse]):
    """The service class for 'form response'."""

    def __init__(
        self,
        *,
        form_response_repository: FormResponseRepository,
        form_repository: FormRepository,
        form_field_repository: FormFieldRepository,
    ) -> None:
        """Initializer for 'form response' service.

        Args:
            form_response_repository (FormResponseRepository): The form response repository.
            form_repository (FormRepository): The form repository.
            form_field_repository (FormFieldRepository): The form field repository.
        """
        self.form_response_repository = form_response_repository
        self.form_repository = form_repository
        self.form_field_repository = form_field_repository
        super().__init__(main_repository=form_response_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[FormResponse]:
        """Get all form response entities.

        Args:
            pagination (str): Pagination parameters.
            filters (str): Filter parameters.
            sort (str): Sort parameters.

        Returns:
            list[FormResponse]: A list of all form response instances.
        """
        return self._default_get_all(
            filters_with_joins=form_response_filters_with_joins,
            filters_without_joins=form_response_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_form_response_filters,
            allowed_sorts=allowed_form_response_sorts,
        )

    def create(self, *, response_data: CreateFormResponseRequestSchema) -> FormResponse:
        """Submit answers for a form, applying conditional logic before storing.

        Args:
            response_data (CreateFormResponseRequestSchema): The response data to submit.

        Returns:
            FormResponse: The stored form response.
        """
        form = self.form_repository.get_by_id(entity_id=response_data.form_id)
        if not form or form.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Form, value=response_data.form_id),
            )

        if form.status != "published":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Form is not published and cannot accept responses.",
            )

        validated_answers = self._validate_and_filter_answers(form=form, answers=response_data.answers)

        try:
            return self.form_response_repository.create(
                data={
                    "form_id": response_data.form_id,
                    "submitted_by": response_data.submitted_by,
                    "answers": validated_answers,
                    "submitted_at": datetime.now(tz=timezone.utc),
                }
            )
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

    def update(self, *args, **kwargs) -> FormResponse:  # type: ignore
        """Not supported for form responses."""
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="Form responses cannot be updated after submission.",
        )

    def get_responses_for_form(self, *, form_id: str) -> list[FormResponse]:
        """Get all responses for a specific form.

        Args:
            form_id (str): The id of the form.

        Returns:
            list[FormResponse]: A list of responses.
        """
        form = self.form_repository.get_by_id(entity_id=form_id)
        if not form or form.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=Form, value=form_id),
            )
        return self.form_response_repository.get_responses_for_form(form_id=form_id)

    def _validate_and_filter_answers(self, *, form: Form, answers: dict) -> dict:
        """Validate answers against form fields and apply conditional logic.

        Fields hidden by conditional logic are stripped from the answers.
        Required visible fields that are missing raise a validation error.

        Args:
            form (Form): The form being submitted.
            answers (dict): The raw answers keyed by field ID.

        Returns:
            dict: The filtered and validated answers.
        """
        all_fields: list[FormField] = []
        for section in form.sections:
            all_fields.extend(section.fields)

        fields_by_id = {field.id: field for field in all_fields}

        visible_field_ids: set[str] = set()
        for field in all_fields:
            conditional = field.conditional_logic
            if conditional:
                depends_on = (
                    conditional.get("depends_on_field")
                    if isinstance(conditional, dict)
                    else getattr(conditional, "depends_on_field", None)
                )
                show_if = (
                    conditional.get("show_if")
                    if isinstance(conditional, dict)
                    else getattr(conditional, "show_if", None)
                )
                answer_for_trigger = answers.get(depends_on)
                if str(answer_for_trigger) == str(show_if):
                    visible_field_ids.add(str(field.id))
            else:
                visible_field_ids.add(str(field.id))

        filtered_answers = {field_id: value for field_id, value in answers.items() if field_id in visible_field_ids}

        for field_id in visible_field_ids:
            field = fields_by_id[field_id]  # type: ignore
            if field and field.required and field_id not in filtered_answers:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Required field '{field.label}' (id: {field_id}) is missing from the submission.",
                )

        return filtered_answers
