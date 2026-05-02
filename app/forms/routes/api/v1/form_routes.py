from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.forms.dependencies.form_service_dependency import create_form_service
from app.forms.docs.form_docs import (
    create_field_docs,
    create_form_docs,
    create_section_docs,
    delete_field_docs,
    delete_form_docs,
    delete_section_docs,
    get_all_forms_docs,
    get_fields_docs,
    get_form_by_id_docs,
    get_sections_docs,
    restore_form_docs,
    update_field_docs,
    update_form_docs,
    update_section_docs,
)
from app.forms.models import Form, FormField, FormSection
from app.forms.schemas.request.form import (
    CreateFormFieldRequestSchema,
    CreateFormRequestSchema,
    CreateFormSectionRequestSchema,
    UpdateFormFieldRequestSchema,
    UpdateFormRequestSchema,
    UpdateFormSectionRequestSchema,
)
from app.forms.schemas.response.form import ReadFormFieldSchema, ReadFormSchema, ReadFormSectionSchema
from app.forms.services.form_service import FormService

form_router = APIRouter(prefix="/forms", tags=["Forms"], dependencies=[Depends(validate_api_key)])


@form_router.post(path="", status_code=status.HTTP_201_CREATED, description=create_form_docs)
def create_form(
    request: Request,
    form_data: CreateFormRequestSchema,
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle creating a new form.

    Args:
        request (Request): The request object.
        form_data (CreateFormRequestSchema): The data needed to create the form.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form = form_service.create(form_data=form_data)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=Form),
        data=ReadFormSchema(**form.to_dict()),
        request=request,
    )


@form_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_forms_docs)
def get_all_forms(
    request: Request,
    form_service: Annotated[FormService, Depends(create_form_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Handle get all forms request.

    Args:
        request (Request): The request object.
        form_service (FormService): The form service to use.
        filters (str): The filters query parameter.
        sort (str): The sort query parameter.
        pagination (str): The pagination query parameter.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    forms = form_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": form_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(forms)})

    response_forms = [ReadFormSchema(**form.to_dict()) for form in forms]

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Form),
        data=response_forms,
        extras=extras,
        request=request,
    )


@form_router.get(path="/{form_id}", status_code=status.HTTP_200_OK, description=get_form_by_id_docs)
def get_form_by_id(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form to get.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle get a form by id request.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form to retrieve.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form = form_service.get_by_id(entity_id=form_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=Form),
        data=ReadFormSchema(**form.to_dict()),
        request=request,
    )


@form_router.put(path="/{form_id}", status_code=status.HTTP_200_OK, description=update_form_docs)
def update_form(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form to update.")],
    data_to_update: UpdateFormRequestSchema,
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle update a form by id request.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form to update.
        data_to_update (UpdateFormRequestSchema): The data to update the form with.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form = form_service.update(form_id=form_id, data_to_update=data_to_update)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=Form),
        data=ReadFormSchema(**form.to_dict()),
        request=request,
    )


@form_router.delete(path="/{form_id}", status_code=status.HTTP_200_OK, description=delete_form_docs)
def delete_form(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form to delete.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle soft-delete a form by id request.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form to delete.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form = form_service.delete(entity_id=form_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=Form),
        data=ReadFormSchema(**form.to_dict()),
        request=request,
    )


@form_router.patch(path="/{form_id}/restore", status_code=status.HTTP_200_OK, description=restore_form_docs)
def restore_form(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form to restore.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle restore a soft-deleted form by id request.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form to restore.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form = form_service.restore(entity_id=form_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.restored_successfully(object_type=Form),
        data=ReadFormSchema(**form.to_dict()),
        request=request,
    )


# ─── Section endpoints ──────────────────────────────────────────────────────

@form_router.post(path="/{form_id}/sections", status_code=status.HTTP_201_CREATED, description=create_section_docs)
def create_section(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form.")],
    section_data: CreateFormSectionRequestSchema,
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle adding a new section to a form.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form.
        section_data (CreateFormSectionRequestSchema): The section data.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    section = form_service.create_section(form_id=form_id, section_data=section_data)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=FormSection),
        data=ReadFormSectionSchema(**section.to_dict()),
        request=request,
    )


@form_router.get(path="/{form_id}/sections", status_code=status.HTTP_200_OK, description=get_sections_docs)
def get_sections(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle get all sections for a form.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    sections = form_service.get_all_sections(form_id=form_id)
    response_sections = [ReadFormSectionSchema(**section.to_dict()) for section in sections]

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormSection),
        data=response_sections,
        request=request,
    )


@form_router.put(path="/sections/{section_id}", status_code=status.HTTP_200_OK, description=update_section_docs)
def update_section(
    request: Request,
    section_id: Annotated[str, Path(..., description="The id of the section to update.")],
    data_to_update: UpdateFormSectionRequestSchema,
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle update a form section by id request.

    Args:
        request (Request): The request object.
        section_id (str): The id of the section to update.
        data_to_update (UpdateFormSectionRequestSchema): The data to update the section with.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    section = form_service.update_section(section_id=section_id, data_to_update=data_to_update)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=FormSection),
        data=ReadFormSectionSchema(**section.to_dict()),
        request=request,
    )


@form_router.delete(path="/sections/{section_id}", status_code=status.HTTP_200_OK, description=delete_section_docs)
def delete_section(
    request: Request,
    section_id: Annotated[str, Path(..., description="The id of the section to delete.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle soft-delete a form section by id request.

    Args:
        request (Request): The request object.
        section_id (str): The id of the section to delete.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    section = form_service.delete_section(section_id=section_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=FormSection),
        data=ReadFormSectionSchema(**section.to_dict()),
        request=request,
    )


# ─── Field endpoints ────────────────────────────────────────────────────────

@form_router.post(path="/sections/{section_id}/fields", status_code=status.HTTP_201_CREATED, description=create_field_docs)
def create_field(
    request: Request,
    section_id: Annotated[str, Path(..., description="The id of the section.")],
    field_data: CreateFormFieldRequestSchema,
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle adding a new field to a section.

    Args:
        request (Request): The request object.
        section_id (str): The id of the section.
        field_data (CreateFormFieldRequestSchema): The field data.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    field = form_service.create_field(section_id=section_id, field_data=field_data)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=FormField),
        data=ReadFormFieldSchema(**field.to_dict()),
        request=request,
    )


@form_router.get(path="/sections/{section_id}", status_code=status.HTTP_200_OK, description=get_sections_docs)
def get_section_by_id(
    request: Request,
    section_id: Annotated[str, Path(..., description="The id of the section to get.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle get a form section by id request.

    Args:
        request (Request): The request object.
        section_id (str): The id of the section to retrieve.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    section = form_service.get_section_by_id(section_id=section_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormSection),
        data=ReadFormSectionSchema(**section.to_dict()),
        request=request,
    )


@form_router.get(path="/sections/{section_id}/fields", status_code=status.HTTP_200_OK, description=get_fields_docs)
def get_fields(
    request: Request,
    section_id: Annotated[str, Path(..., description="The id of the section.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle get all fields for a section.

    Args:
        request (Request): The request object.
        section_id (str): The id of the section.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    fields = form_service.get_all_fields(section_id=section_id)
    response_fields = [ReadFormFieldSchema(**field.to_dict()) for field in fields]

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormField),
        data=response_fields,
        request=request,
    )


@form_router.get(path="/fields/{field_id}", status_code=status.HTTP_200_OK, description=get_fields_docs)
def get_field_by_id(
    request: Request,
    field_id: Annotated[str, Path(..., description="The id of the field to get.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle get a form field by id request.

    Args:
        request (Request): The request object.
        field_id (str): The id of the field to retrieve.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    field = form_service.get_field_by_id(field_id=field_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormField),
        data=ReadFormFieldSchema(**field.to_dict()),
        request=request,
    )


@form_router.put(path="/fields/{field_id}", status_code=status.HTTP_200_OK, description=update_field_docs)
def update_field(
    request: Request,
    field_id: Annotated[str, Path(..., description="The id of the field to update.")],
    data_to_update: UpdateFormFieldRequestSchema,
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle update a form field by id request.

    Args:
        request (Request): The request object.
        field_id (str): The id of the field to update.
        data_to_update (UpdateFormFieldRequestSchema): The data to update the field with.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    field = form_service.update_field(field_id=field_id, data_to_update=data_to_update)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.updated_successfully(object_type=FormField),
        data=ReadFormFieldSchema(**field.to_dict()),
        request=request,
    )


@form_router.delete(path="/fields/{field_id}", status_code=status.HTTP_200_OK, description=delete_field_docs)
def delete_field(
    request: Request,
    field_id: Annotated[str, Path(..., description="The id of the field to delete.")],
    form_service: Annotated[FormService, Depends(create_form_service)],
) -> ResponseSchema:
    """Handle soft-delete a form field by id request.

    Args:
        request (Request): The request object.
        field_id (str): The id of the field to delete.
        form_service (FormService): The form service to use.

    Returns:
        ResponseSchema: The response data.
    """
    field = form_service.delete_field(field_id=field_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=FormField),
        data=ReadFormFieldSchema(**field.to_dict()),
        request=request,
    )
