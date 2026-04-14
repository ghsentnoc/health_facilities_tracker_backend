from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request, status

from app.auth.dependencies.auth_dependency import validate_api_key
from app.core.docs.root_docs import read_root_docs
from app.core.schemas.base_entity_response_schema import ResponseSchema
from app.core.utils.allowed_filters_sort import allowed_filters, allowed_sorts
from app.core.utils.constants import HTTPResponseStatus
from app.core.utils.general import process_filter_sort_and_pagination
from app.core.utils.messages import SuccessMessages

root_api_router = APIRouter(prefix="", tags=["Root"], dependencies=[Depends(validate_api_key)])


@root_api_router.get(path="/", status_code=status.HTTP_200_OK, description=read_root_docs)
async def read_root(
    request: Request,
    filters: Annotated[Optional[str], Query(..., description="Filters query parameter")] = None,
    sort: Annotated[Optional[str], Query(..., description="Sort query parameter")] = None,
    pagination: Annotated[Optional[str], Query(..., description="Pagination query parameter")] = None,
) -> ResponseSchema:
    """Root endpoint returning a simple JSON response.

    Args:
        request (Request): The request object.
        filters (str): The filters query parameter
        sort (str): The sort query parameter
        pagination (str): The pagination query parameter

    Returns:
        dict[str, str]: A dictionary with a greeting message.
    """
    processed_filters, processed_sorts, pagination_result = process_filter_sort_and_pagination(
        filters=filters,
        sort=sort,
        pagination=pagination,
        allowed_filters=allowed_filters,
        allowed_sorts=allowed_sorts,
    )

    response_data = ResponseSchema(
        status=HTTPResponseStatus.SUCCESS.value,
        status_code=status.HTTP_200_OK,
        message=SuccessMessages.retrieved_successfully(object_type=type("Root")),  # type: ignore
        extras={
            "processed_filters": processed_filters,
            "processed_sorts": processed_sorts,
            "pagination": pagination_result,
        },
        request=request,
    )

    return response_data
