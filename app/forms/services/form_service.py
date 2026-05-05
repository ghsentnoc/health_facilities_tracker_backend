from typing import Optional

from fastapi import HTTPException, status

from app.core.custom_exceptions import ObjectAlreadyExistsException
from app.core.services.base_service import BaseService
from app.core.utils.messages import ErrorMessages
from app.forms.models import Form, FormField, FormSection
from app.forms.repositories import FormFieldRepository, FormRepository, FormSectionRepository
from app.forms.schemas.request.form import (
    CreateFormFieldRequestSchema,
    CreateFormRequestSchema,
    CreateFormSectionRequestSchema,
    UpdateFormFieldRequestSchema,
    UpdateFormRequestSchema,
    UpdateFormSectionRequestSchema,
)
from app.forms.utils.allowed_filters_sort import (
    allowed_form_filters,
    allowed_form_sorts,
    form_filters_with_joins,
    form_filters_without_joins,
)


class FormService(BaseService[Form]):
    """The service class for 'form'."""

    def __init__(
        self,
        *,
        form_repository: FormRepository,
        form_section_repository: FormSectionRepository,
        form_field_repository: FormFieldRepository,
    ) -> None:
        """Initializer for 'form' service.

        Args:
            form_repository (FormRepository): The form repository.
            form_section_repository (FormSectionRepository): The form section repository.
            form_field_repository (FormFieldRepository): The form field repository.
        """
        self.form_repository = form_repository
        self.form_section_repository = form_section_repository
        self.form_field_repository = form_field_repository
        super().__init__(main_repository=form_repository)

    def get_all(
        self, *, pagination: Optional[str] = None, filters: Optional[str] = None, sort: Optional[str] = None
    ) -> list[Form]:
        """Get all form entities.

        Args:
            pagination (str): Pagination parameters.
            filters (str): Filter parameters.
            sort (str): Sort parameters.

        Returns:
            list[Form]: A list of all form instances.
        """
        return self._default_get_all(
            filters_with_joins=form_filters_with_joins,
            filters_without_joins=form_filters_without_joins,
            pagination=pagination,
            filters=filters,
            sort=sort,
            allowed_filters=allowed_form_filters,
            allowed_sorts=allowed_form_sorts,
        )

    def create(self, *, form_data: CreateFormRequestSchema, created_by: Optional[str] = None) -> Form:
        """Create a new form along with its sections and fields.

        Args:
            form_data (CreateFormRequestSchema): The form data to create.
            created_by (str, optional): The ID of the user creating the form.

        Returns:
            Form: The newly created form.
        """
        try:
            form = self.form_repository.create(
                data={
                    "title": form_data.title,
                    "description": form_data.description,
                    "status": form_data.status,
                    "created_by": created_by,
                }
            )
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        if form_data.sections:
            for section_data in form_data.sections:
                self._create_section_with_fields(form_id=str(form.id), section_data=section_data)

        return self.form_repository.get_by_id(entity_id=form.id)  # type: ignore

    def update(self, *, form_id: str, data_to_update: UpdateFormRequestSchema) -> Form:
        """Update an existing form.

        Args:
            form_id (str): The id of the form to update.
            data_to_update (UpdateFormRequestSchema): The data to update the form with.

        Returns:
            Form: The updated form.
        """
        form = self.get_by_id(entity_id=form_id)

        try:
            self.form_repository.update(
                entity=form,
                update_data=data_to_update.model_dump(exclude_none=True),
            )
        except ObjectAlreadyExistsException as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e

        return self.form_repository.get_by_id(entity_id=form_id)  # type: ignore

    def get_all_sections(
        self,
        *,
        form_id: str,
        pagination: Optional[str] = None,
        filters: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> list[FormSection]:
        """Get all sections for a form.

        Args:
            form_id (str): The id of the form.
            pagination (str): Pagination parameters.
            filters (str): Filter parameters.
            sort (str): Sort parameters.

        Returns:
            list[FormSection]: A list of all section instances.
        """
        _ = self.get_by_id(entity_id=form_id)
        return self.form_section_repository.get_sections_for_form(form_id=form_id)

    def get_section_by_id(self, *, section_id: str) -> FormSection:
        """Get a form section by its id.

        Args:
            section_id (str): The id of the section.

        Returns:
            FormSection: The section instance.
        """
        section = self.form_section_repository.get_by_id(entity_id=section_id)
        if not section or section.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormSection, value=section_id),
            )
        return section

    def get_field_by_id(self, *, field_id: str) -> FormField:
        """Get a form field by its id.

        Args:
            field_id (str): The id of the field.

        Returns:
            FormField: The field instance.
        """
        field = self.form_field_repository.get_by_id(entity_id=field_id)
        if not field or field.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormField, value=field_id),
            )
        return field

    def create_section(self, *, form_id: str, section_data: CreateFormSectionRequestSchema) -> FormSection:
        """Create a new section for a form.

        Args:
            form_id (str): The id of the form.
            section_data (CreateFormSectionRequestSchema): The section data.

        Returns:
            FormSection: The newly created section.
        """
        _ = self.get_by_id(entity_id=form_id)
        return self._create_section_with_fields(form_id=form_id, section_data=section_data)

    def update_section(self, *, section_id: str, data_to_update: UpdateFormSectionRequestSchema) -> FormSection:
        """Update an existing form section.

        Args:
            section_id (str): The id of the section to update.
            data_to_update (UpdateFormSectionRequestSchema): The data to update with.

        Returns:
            FormSection: The updated section.
        """
        section = self.form_section_repository.get_by_id(entity_id=section_id)
        if not section or section.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormSection, value=section_id),
            )
        return self.form_section_repository.update(
            entity=section,
            update_data=data_to_update.model_dump(exclude_none=True),
        )

    def delete_section(self, *, section_id: str) -> FormSection:
        """Soft-delete a form section.

        Args:
            section_id (str): The id of the section to delete.

        Returns:
            FormSection: The deleted section.
        """
        section = self.form_section_repository.get_by_id(entity_id=section_id)
        if not section or section.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormSection, value=section_id),
            )
        return self.form_section_repository.delete(entity_to_delete=section)

    def get_all_fields(
        self,
        *,
        section_id: str,
        pagination: Optional[str] = None,
        filters: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> list[FormField]:
        """Get all fields for a section.

        Args:
            section_id (str): The id of the section.
            pagination (str): Pagination parameters.
            filters (str): Filter parameters.
            sort (str): Sort parameters.

        Returns:
            list[FormField]: A list of all field instances.
        """
        section = self.form_section_repository.get_by_id(entity_id=section_id)
        if not section or section.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormSection, value=section_id),
            )
        return self.form_field_repository.get_fields_for_section(section_id=section_id)

    def create_field(self, *, section_id: str, field_data: CreateFormFieldRequestSchema) -> FormField:
        """Create a new field within a section.

        Args:
            section_id (str): The id of the section.
            field_data (CreateFormFieldRequestSchema): The field data.

        Returns:
            FormField: The newly created field.
        """
        section = self.form_section_repository.get_by_id(entity_id=section_id)
        if not section or section.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormSection, value=section_id),
            )

        field_dict = field_data.model_dump()
        validation = field_dict.pop("validation", None)
        conditional_logic = field_dict.pop("conditional_logic", None)

        return self.form_field_repository.create(
            data={
                **field_dict,
                "section_id": section_id,
                "form_id": section.form_id,
                "validation": validation,
                "conditional_logic": conditional_logic,
            }
        )

    def update_field(self, *, field_id: str, data_to_update: UpdateFormFieldRequestSchema) -> FormField:
        """Update an existing form field.

        Args:
            field_id (str): The id of the field to update.
            data_to_update (UpdateFormFieldRequestSchema): The data to update with.

        Returns:
            FormField: The updated field.
        """
        field = self.form_field_repository.get_by_id(entity_id=field_id)
        if not field or field.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormField, value=field_id),
            )

        update_dict = data_to_update.model_dump(exclude_none=True)
        if "validation" in update_dict and update_dict["validation"] is not None:
            update_dict["validation"] = update_dict["validation"]
        if "conditional_logic" in update_dict and update_dict["conditional_logic"] is not None:
            update_dict["conditional_logic"] = update_dict["conditional_logic"]

        return self.form_field_repository.update(entity=field, update_data=update_dict)

    def delete_field(self, *, field_id: str) -> FormField:
        """Soft-delete a form field.

        Args:
            field_id (str): The id of the field to delete.

        Returns:
            FormField: The deleted field.
        """
        field = self.form_field_repository.get_by_id(entity_id=field_id)
        if not field or field.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ErrorMessages.entity_does_not_exists(entity_type=FormField, value=field_id),
            )
        return self.form_field_repository.delete(entity_to_delete=field)

    def _create_section_with_fields(self, *, form_id: str, section_data: CreateFormSectionRequestSchema) -> FormSection:
        """Internal helper to create a section and its fields.

        Args:
            form_id (str): The id of the form.
            section_data (CreateFormSectionRequestSchema): The section data.

        Returns:
            FormSection: The newly created section.
        """
        section = self.form_section_repository.create(
            data={
                "form_id": form_id,
                "title": section_data.title,
                "description": section_data.description,
                "order": section_data.order,
            }
        )

        if section_data.fields:
            for field_data in section_data.fields:
                field_dict = field_data.model_dump()
                validation = field_dict.pop("validation", None)
                conditional_logic = field_dict.pop("conditional_logic", None)
                self.form_field_repository.create(
                    data={
                        **field_dict,
                        "section_id": section.id,
                        "form_id": form_id,
                        "validation": validation,
                        "conditional_logic": conditional_logic,
                    }
                )

        return section
