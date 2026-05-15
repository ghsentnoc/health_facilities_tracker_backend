import json
from typing import Any, Callable, Optional, Union

from fastapi import HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.orm import Query

from app.core.custom_exceptions import (
    InvalidFilterError,
    InvalidFilterOperatorError,
    InvalidPaginationOptionError,
    InvalidPaginationValueError,
    InvalidQueryParamsJSONFormatError,
    InvalidSortError,
    InvalidSortModeError,
)
from app.core.schemas.query_params_schemas import AllowedFilterSchema, AllowedSortSchema, FilterSchema, PaginationSchema
from app.core.utils.constants import PaginationConstants
from app.core.utils.messages import ErrorMessages
from app.core.utils.model_map import MODEL_MAP
from app.database.base import Base


def offset_calculator(*, page: int, page_size: int) -> int:
    """Calculate the offset for pagination.

    Args:
        page (int): The current page number.
        page_size (int): The number of items per page.

    Returns:
        int: The calculated offset.
    """
    # check if page or page_size is greater than 0 else set default value
    page = page if page > 0 else PaginationConstants.DEFAULT_PAGE.value
    page_size = page_size if page_size > 0 else PaginationConstants.DEFAULT_PAGE_SIZE.value

    # calculate the offset
    return (page - 1) * page_size


def filters_processor(*, filters: Optional[str], allowed_filters: list[AllowedFilterSchema]) -> dict:
    """Process the filters sent from a request.

    Args:
        filters (dict): The filters to process
        allowed_filters (list[dict]): The allowed list of filters.

    Returns:
        dict: The processed filters
    Raises:
        InvalidQueryParamsJSONFormatError: if the filter query param is not a valid json
        InvalidFilterError: if the filter is not allowed
        InvalidFilterOperatorError: if the operator on a filter is not allowed
    """
    if not filters:
        return {}

    # load filters to a dictionary
    try:
        filter_dict = json.loads(filters)
    except json.JSONDecodeError as e:
        raise InvalidQueryParamsJSONFormatError(
            ErrorMessages.invalid_json_format_for_query_params(query_param="filters")
        ) from e

    # extract all allowed fields from allowed_filters
    allowed_filters_fields = [allowed_filter.field for allowed_filter in allowed_filters]
    processed_filters = {}

    # check if filters passed from request are allowed
    for _field in filter_dict.keys():
        if _field not in allowed_filters_fields:
            raise InvalidFilterError(ErrorMessages.invalid_filter_or_sort(filter_or_sort_field=_field))

    # check if the operator for each filter is valid
    # loop over filters sent from request
    for _field, values in filter_dict.items():
        # check if the field is deleted and the value is none continue
        if _field == "is_deleted" and values["value"] is None:
            continue

        if _field == "is_deleted" and values["value"]:
            if values["value"] not in [True, False]:
                raise InvalidFilterError("is_deleted can be 'true' or 'false' or 'null' valid json type.")
        # create filter schema
        filter_field_schema = FilterSchema(**values)

        # check if operator exists
        if filter_field_schema.operator:
            # loop over the allowed filters
            for allowed_filter in allowed_filters:
                # convert all operators to lowercase
                # allowed_filter.operators = [operator.lower() for operator in allowed_filter.operators]

                # check if current field of request filter is same as current field in allowed filter
                if allowed_filter.field == _field:
                    # convert current request filter operator to lowercase
                    # filter_field_schema.operator = filter_field_schema.operator.lower()

                    # if the current request filter operator is not in the current allowed filters operator
                    # raise an error
                    if filter_field_schema.operator not in allowed_filter.operators:
                        raise InvalidFilterOperatorError(
                            ErrorMessages.invalid_operator(operator=filter_field_schema.operator, filter_name=_field)
                        )

        # if all checks pass, append to processed filters list
        processed_filters[_field] = filter_field_schema.model_dump()

    return processed_filters


def sort_processor(*, sort: Optional[str], allowed_sorts: list[AllowedSortSchema]) -> dict:
    """Process the filters sent from a request.

    Args:
        sort (dict): The sort to process
        allowed_sorts (list[dict]): The allowed list of sorts.

    Returns:
        dict: The processed sorts
    Raises:
        InvalidQueryParamsJSONFormatError: if the sort query param is not a valid json
        InvalidSortError: if the sort is not allowed
        InvalidSortModeError: if the mode on a sort is not allowed
    """
    if not sort:
        return {}

    processed_sorts = {}

    # load filters to a dictionary
    try:
        sort_dict = json.loads(sort)
    except json.JSONDecodeError as e:
        raise InvalidQueryParamsJSONFormatError(
            ErrorMessages.invalid_json_format_for_query_params(query_param="sort")
        ) from e

    # check if sorts passed from request are allowed
    for _field in sort_dict.keys():
        # extract all allowed fields from allowed_sorts
        allowed_sorts_fields = [allowed_sort.field for allowed_sort in allowed_sorts]

        # check if field is in allowed sorts fields
        if _field not in allowed_sorts_fields:
            raise InvalidSortError(ErrorMessages.invalid_filter_or_sort(filter_or_sort_field=_field))

    # check if the mode for each sort is valid
    # loop over sorts sent from request
    for _field, _value in sort_dict.items():
        # loop over the allowed sorts
        for allowed_sort in allowed_sorts:
            # check if current field of request sort is same as current field in allowed sort
            if allowed_sort.field == _field:
                # convert current request sort mode to lowercase
                _value = _value.lower()

                # if the current request sort mode is not the same as the current allowed sort mode
                # raise an error
                # else break the loop
                if _value not in allowed_sort.mode:
                    raise InvalidSortModeError(ErrorMessages.invalid_mode_for_sort(sort_mode=_value))
                else:
                    break

        processed_sorts[_field] = _value

    return processed_sorts


def pagination_processor(*, pagination: Optional[str]) -> dict:
    """Process the pagination sent from a request.

    Args:
        pagination (dict): The pagination to process

    Returns:
        dict[str, int]: The processed pagination
    """
    if not pagination:
        return {}

    # load pagination to a dictionary
    try:
        pagination_dict = json.loads(pagination)
    except json.JSONDecodeError as e:
        raise InvalidQueryParamsJSONFormatError(
            ErrorMessages.invalid_json_format_for_query_params(query_param="pagination")
        ) from e

    # check if page or page_size is in pagination_dict
    if "page" not in pagination_dict and "page_size" not in pagination_dict:
        raise InvalidPaginationOptionError(ErrorMessages.missing_required_query_param(query_param="page or page_size"))

    # set default values if page or page_size is not in pagination_dict
    if pagination_dict.get("page") is None:
        pagination_dict["page"] = PaginationConstants.DEFAULT_PAGE.value

    # set default values if page or page_size is not in pagination_dict
    if pagination_dict.get("page_size") is None:
        pagination_dict["page_size"] = PaginationConstants.DEFAULT_PAGE_SIZE.value

    # check if pagination values are digits and greater  than 0
    if (
        not str(pagination_dict.get("page")).isdigit()
        or not str(pagination_dict.get("page_size")).isdigit()
        or int(pagination_dict.get("page")) <= 0
        or int(pagination_dict.get("page_size")) <= 0
    ):
        raise InvalidPaginationValueError(ErrorMessages.INVALID_PAGINATION_VALUES.value)

    pagination_result = PaginationSchema(**pagination_dict)
    return pagination_result.model_dump()


def process_filter_sort_and_pagination(
    *,
    filters: Optional[str],
    sort: Optional[str],
    pagination: Optional[str],
    allowed_filters: list[AllowedFilterSchema],
    allowed_sorts: list[AllowedSortSchema],
) -> tuple[dict, dict, dict]:
    """Process filters, sorts and pagination sent from a request.

    Args:
        filters (str): The filters to process
        sort (str): The sort to process
        pagination (str): The pagination to process
        allowed_filters (list[dict]): The allowed list of filters.
        allowed_sorts (list[dict]): The allowed list of sorts.

    Returns:
        tuple: The processed filters, sorts and pagination
    """
    processed_filters: dict = {}
    processed_sorts: dict = {}
    pagination_result: dict = {}

    try:
        if filters:
            processed_filters = filters_processor(filters=filters, allowed_filters=allowed_filters)

        if sort:
            processed_sorts = sort_processor(sort=sort, allowed_sorts=allowed_sorts)

        if pagination:
            pagination_result = pagination_processor(pagination=pagination)
    except (
        InvalidQueryParamsJSONFormatError,
        InvalidFilterError,
        InvalidFilterOperatorError,
        InvalidSortError,
        InvalidSortModeError,
        InvalidPaginationOptionError,
        InvalidPaginationValueError,
    ) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return processed_filters, processed_sorts, pagination_result


def map_operator_to_function(*, operator: str) -> Callable:
    """Map an operator to a function.

    Args:
        operator (str): The operator on the field to map.

    Returns:
        Callable: The mapped operator function.
    """
    operator_map = {
        "eq": lambda col, val: col == val,
        "lt": lambda col, val: col < val,
        "le": lambda col, val: col <= val,
        "gt": lambda col, val: col > val,
        "ge": lambda col, val: col >= val,
        "like": lambda col, val: col.ilike(f"%{val}%"),
        "ne": lambda col, val: col != val,
    }

    if operator not in operator_map:
        raise InvalidFilterOperatorError("Operator is invalid.")

    filter_fn = operator_map[operator]

    return filter_fn


def sort_mapper(*, sort_mode: str) -> Any:
    """Map sort mode to sqlalchemy sort order.

    sort_mode (str): The sort mode to order in.
    """
    _sort_mapper = {"asc": asc, "desc": desc}

    return _sort_mapper.get(sort_mode, asc)


def apply_filters_with_no_joins(*, query: Query, model: Base, filters: dict, filters_without_joins: list) -> Query:
    """Apply filters without joins to a model.

    Args:
        query (Query): The query to apply filters on.
        model (Base): The model to apply filters to.
        filters (dict): The filters to check and apply.
        filters_without_joins (list): The list of filters that do not need joins.

    Returns:
        Query: The query response of filters without joins.
    """
    # loop through filters without joins
    # if any of the fields in the filters without joins is in filters from the request
    # set the column to filter by
    # map the operator to the right function
    # apply filter on query
    # return the query
    for field in filters_without_joins:
        if field in filters:
            column = getattr(model, field)
            operator_func = map_operator_to_function(operator=filters[field]["operator"])
            query = query.filter(operator_func(column, filters[field]["value"]))

    return query


def apply_filters_with_joins(*, query: Query, filters: dict, filters_with_joins: list) -> Query:
    """Apply filters with joins to a query.

        filters (dict): The filters to check and apply.
        filters_with_joins (list): The list of filters that need joins.

    Returns:
        Query: The query response of filters without joins.
    """
    # loop through filters without joins
    # if any of the fields in the filters with joins is in filters from the request
    # set the column to filter by
    # map the operator to the right function
    # apply filter on query
    # return the query
    for field in filters_with_joins:
        if field in filters:
            column = getattr(filters[field]["model"], filters[field]["field_name"])
            operator_func = map_operator_to_function(operator=filters[field]["operator"])
            query = query.filter(operator_func(column, filters[field]["value"]))

    return query


def apply_sort(*, query: Query, sort_items: dict, model: Base) -> Query:
    """Apply sort to a query.

    Args:
        query (Query): The query to apply the sort on.
        sort_items (dict): The sort items to apply.
        model (Base): The model to apply the sort on.

    Returns:
        Query: The query response after sort being applied.
    """
    for field, direction in sort_items.items():
        if hasattr(model, field):
            query = query.order_by(sort_mapper(sort_mode=direction)(getattr(model, field)))

    if "joined_sort" in sort_items:
        for item in sort_items["joined_sort"]:
            if hasattr(MODEL_MAP[item.model], item.field):
                query = query.order_by(
                    sort_mapper(sort_mode=item.direction)(getattr(MODEL_MAP[item.model], item.field))
                )

    return query


def next_page(page: int, total_pages: int) -> Union[int, None]:
    """Get the next page

    Args:
        page (int): The current page
        total_pages (int): The total number of pages

    Returns:
        Union[int, None]: The next page or None
    """
    return page + 1 if total_pages > page else None


def previous_page(page: int) -> Union[int, None]:
    """Get the previous page

    Args:
        page (int): The current page

    Returns:
        Union[int, None]: The previous page or None
    """
    return page - 1 if page > 1 else None
