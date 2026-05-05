from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.messages import SuccessMessages
from app.forms.dependencies.form_response_service_dependency import create_form_response_service
from app.forms.docs.form_response_docs import (
    delete_response_docs,
    get_all_responses_docs,
    get_response_by_id_docs,
    get_responses_for_form_docs,
    submit_form_response_docs,
)
from app.forms.models import FormResponse
from app.forms.schemas.request.form_response import CreateFormResponseRequestSchema
from app.forms.schemas.response.form_response import ReadFormResponseSchema
from app.forms.services.form_response_service import FormResponseService

form_response_router = APIRouter(
    prefix="/form-responses", tags=["Form Responses"], dependencies=[Depends(validate_api_key)]
)


@form_response_router.post(path="", status_code=status.HTTP_201_CREATED, description=submit_form_response_docs)
def submit_form_response(
    request: Request,
    response_data: CreateFormResponseRequestSchema,
    form_response_service: Annotated[FormResponseService, Depends(create_form_response_service)],
) -> ResponseSchema:
    """Handle submitting a form response.

    Args:
        request (Request): The request object.
        response_data (CreateFormResponseRequestSchema): The form submission data.
        form_response_service (FormResponseService): The form response service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form_response = form_response_service.create(response_data=response_data)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_201_CREATED,
        message=SuccessMessages.created_successfully(object_type=FormResponse),
        data=ReadFormResponseSchema(**form_response.to_dict()),
        request=request,
    )


@form_response_router.get(path="", status_code=status.HTTP_200_OK, description=get_all_responses_docs)
def get_all_form_responses(
    request: Request,
    form_response_service: Annotated[FormResponseService, Depends(create_form_response_service)],
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Handle get all form responses request.

    Args:
        request (Request): The request object.
        form_response_service (FormResponseService): The form response service to use.
        filters (str): The filters query parameter.
        sort (str): The sort query parameter.
        pagination (str): The pagination query parameter.

    Returns:
        ResponseSchema: The response data.
    """
    extras: dict = {}
    responses = form_response_service.get_all(pagination=pagination, filters=filters, sort=sort)
    extras.update({"pagination": form_response_service.get_pagination_extras(request=request)})
    extras["pagination"].update({"total_retrieved": len(responses)})

    response_list = [ReadFormResponseSchema(**r.to_dict()) for r in responses]

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormResponse),
        data=response_list,
        extras=extras,
        request=request,
    )


@form_response_router.get(path="/{response_id}", status_code=status.HTTP_200_OK, description=get_response_by_id_docs)
def get_form_response_by_id(
    request: Request,
    response_id: Annotated[str, Path(..., description="The id of the form response to get.")],
    form_response_service: Annotated[FormResponseService, Depends(create_form_response_service)],
) -> ResponseSchema:
    """Handle get a form response by id request.

    Args:
        request (Request): The request object.
        response_id (str): The id of the form response.
        form_response_service (FormResponseService): The form response service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form_response = form_response_service.get_by_id(entity_id=response_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormResponse),
        data=ReadFormResponseSchema(**form_response.to_dict()),
        request=request,
    )


@form_response_router.get(
    path="/form/{form_id}", status_code=status.HTTP_200_OK, description=get_responses_for_form_docs
)
def get_responses_for_form(
    request: Request,
    form_id: Annotated[str, Path(..., description="The id of the form.")],
    form_response_service: Annotated[FormResponseService, Depends(create_form_response_service)],
) -> ResponseSchema:
    """Handle get all responses for a specific form.

    Args:
        request (Request): The request object.
        form_id (str): The id of the form.
        form_response_service (FormResponseService): The form response service to use.

    Returns:
        ResponseSchema: The response data.
    """
    responses = form_response_service.get_responses_for_form(form_id=form_id)
    response_list = [ReadFormResponseSchema(**r.to_dict()) for r in responses]

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=FormResponse),
        data=response_list,
        request=request,
    )


@form_response_router.delete(path="/{response_id}", status_code=status.HTTP_200_OK, description=delete_response_docs)
def delete_form_response(
    request: Request,
    response_id: Annotated[str, Path(..., description="The id of the form response to delete.")],
    form_response_service: Annotated[FormResponseService, Depends(create_form_response_service)],
) -> ResponseSchema:
    """Handle soft-delete a form response by id request.

    Args:
        request (Request): The request object.
        response_id (str): The id of the form response to delete.
        form_response_service (FormResponseService): The form response service to use.

    Returns:
        ResponseSchema: The response data.
    """
    form_response = form_response_service.delete(entity_id=response_id)

    return ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.deleted_successfully(object_type=FormResponse),
        data=ReadFormResponseSchema(**form_response.to_dict()),
        request=request,
    )
