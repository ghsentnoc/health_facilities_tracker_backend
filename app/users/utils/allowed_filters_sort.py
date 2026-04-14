from app.core.schemas.query_params_schemas import AllowedFilterSchema, AllowedSortSchema
from app.core.utils.allowed_filters_sort import created_at_filter, created_at_sort, is_deleted_filter, is_deleted_sort

########################### user filters without joins ############################
user_filters_without_joins = ["email", "created_at", "deleted_at", "is_suspended", "is_verified"]

########################### user filters with joins ###############################
user_filters_with_joins = ["first_name", "phone_number", "facility_name", "country", "role"]


############################ allowed user filters #################################
user_email_filter = AllowedFilterSchema(field="email", operators=["eq"])
user_first_name_filter = AllowedFilterSchema(field="first_name", operators=["eq", "like"])
user_phone_number_filter = AllowedFilterSchema(field="phone_number", operators=["eq"])
user_facility_name_filter = AllowedFilterSchema(field="facility_name", operators=["eq", "like"])
user_country_filter = AllowedFilterSchema(field="country", operators=["eq", "like"])
user_role_filter = AllowedFilterSchema(field="role", operators=["eq", "like"])
allowed_user_filters = [
    user_email_filter,
    user_first_name_filter,
    user_phone_number_filter,
    user_facility_name_filter,
    user_country_filter,
    user_role_filter,
    created_at_filter,
    is_deleted_filter,
]

############################# allowed user sorts ###################################
user_email_sort = AllowedSortSchema(field="email")
allowed_user_sorts = [user_email_sort, created_at_sort, is_deleted_sort]
