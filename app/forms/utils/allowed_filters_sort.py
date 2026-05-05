from app.core.schemas.query_params_schemas import AllowedFilterSchema, AllowedSortSchema
from app.core.utils.allowed_filters_sort import created_at_filter, created_at_sort, is_deleted_filter, is_deleted_sort

#################################### filters without joins ##################################
form_filters_without_joins = ["title", "status", "created_by", "created_at", "is_deleted"]
form_section_filters_without_joins = ["title", "form_id", "created_at", "is_deleted"]
form_field_filters_without_joins = [
    "label",
    "field_type",
    "required",
    "section_id",
    "form_id",
    "created_at",
    "is_deleted",
]
form_response_filters_without_joins = ["form_id", "submitted_by", "submitted_at", "created_at", "is_deleted"]

#################################### filters with joins ######################################
form_filters_with_joins: list = []
form_section_filters_with_joins: list = []
form_field_filters_with_joins: list = []
form_response_filters_with_joins: list = []

################################### allowed form filters ###################################
form_title_filter = AllowedFilterSchema(field="title", operators=["eq", "like"])
form_status_filter = AllowedFilterSchema(field="status", operators=["eq"])
form_created_by_filter = AllowedFilterSchema(field="created_by", operators=["eq"])
allowed_form_filters = [
    form_title_filter,
    form_status_filter,
    form_created_by_filter,
    created_at_filter,
    is_deleted_filter,
]

################################### allowed form sorts ###################################
form_title_sort = AllowedSortSchema(field="title")
form_status_sort = AllowedSortSchema(field="status")
allowed_form_sorts = [form_title_sort, form_status_sort, created_at_sort, is_deleted_sort]

################################### allowed form section filters ###################################
form_section_title_filter = AllowedFilterSchema(field="title", operators=["eq", "like"])
form_section_form_id_filter = AllowedFilterSchema(field="form_id", operators=["eq"])
allowed_form_section_filters = [
    form_section_title_filter,
    form_section_form_id_filter,
    created_at_filter,
    is_deleted_filter,
]

################################### allowed form section sorts ###################################
form_section_title_sort = AllowedSortSchema(field="title")
allowed_form_section_sorts = [form_section_title_sort, created_at_sort, is_deleted_sort]

################################### allowed form field filters ###################################
form_field_label_filter = AllowedFilterSchema(field="label", operators=["eq", "like"])
form_field_type_filter = AllowedFilterSchema(field="field_type", operators=["eq"])
form_field_required_filter = AllowedFilterSchema(field="required", operators=["eq"])
form_field_section_id_filter = AllowedFilterSchema(field="section_id", operators=["eq"])
form_field_form_id_filter = AllowedFilterSchema(field="form_id", operators=["eq"])
allowed_form_field_filters = [
    form_field_label_filter,
    form_field_type_filter,
    form_field_required_filter,
    form_field_section_id_filter,
    form_field_form_id_filter,
    created_at_filter,
    is_deleted_filter,
]

################################### allowed form field sorts ###################################
form_field_label_sort = AllowedSortSchema(field="label")
form_field_order_sort = AllowedSortSchema(field="order")
allowed_form_field_sorts = [form_field_label_sort, form_field_order_sort, created_at_sort, is_deleted_sort]

################################### allowed form response filters ###################################
form_response_form_id_filter = AllowedFilterSchema(field="form_id", operators=["eq"])
form_response_submitted_by_filter = AllowedFilterSchema(field="submitted_by", operators=["eq"])
allowed_form_response_filters = [
    form_response_form_id_filter,
    form_response_submitted_by_filter,
    created_at_filter,
    is_deleted_filter,
]

################################### allowed form response sorts ###################################
form_response_submitted_at_sort = AllowedSortSchema(field="submitted_at")
allowed_form_response_sorts = [form_response_submitted_at_sort, created_at_sort, is_deleted_sort]
