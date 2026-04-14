from app.core.schemas.query_params_schemas import AllowedFilterSchema, AllowedSortSchema
from app.core.utils.allowed_filters_sort import created_at_filter, created_at_sort, is_deleted_filter, is_deleted_sort

##################### filters without joins ##############################################
role_filters_without_joins = ["name", "created_at", "is_deleted"]
permission_filters_without_joins = role_filters_without_joins.copy()
refresh_token_filters_without_joins = [
    "user_id",
    "token",
    "revoked",
    "revoked_reason",
    "expires_at",
    "created_at",
    "is_deleted",
]


################### filters with joins ############################################3
application_api_keys_filters_with_joins = ["app_name"]

################################### allowed role filters ###############################
role_name_filter = AllowedFilterSchema(field="name", operators=["eq", "like"])
allowed_role_filters = [role_name_filter, created_at_filter, is_deleted_filter]

################################### allowed permission filters ############################
allowed_permission_filters = allowed_role_filters.copy()

################################### allowed refresh token filters ############################
user_id_filter = AllowedFilterSchema(field="user_id", operators=["eq", "like"])
token_filter = AllowedFilterSchema(field="token", operators=["eq", "like"])
revoked_filter = AllowedFilterSchema(field="revoked", operators=["eq"])
revoked_reason_filter = AllowedFilterSchema(field="revoked_reason", operators=["eq", "like"])
expires_at_filter = AllowedFilterSchema(field="expires_at", operators=["eq", "lt", "le", "gt", "ge"])
allowed_refresh_token_filters = [
    user_id_filter,
    token_filter,
    revoked_filter,
    revoked_reason_filter,
    expires_at_filter,
    created_at_filter,
    is_deleted_filter,
]

################################### allowed role sorts ####################################
role_name_sort = AllowedSortSchema(field="name")
allowed_role_sorts = [role_name_sort, created_at_sort, is_deleted_sort]

################################ allowed permission sorts ################################
allowed_permission_sorts = allowed_role_sorts.copy()

############################### allowed refresh token sorts ##############################
expires_at_sort = AllowedSortSchema(field="expires_at")
allowed_refresh_token_sorts = [expires_at_sort, created_at_sort, is_deleted_sort]


############################## application registration filters without joins ###########################
application_registration_filters_without_joins = [
    "app_name",
    "platform",
    "is_active",
    "created_at",
    "is_deleted",
    "deleted_at",
]

############################ allowed application registration filters ###################################
app_name_filter = AllowedFilterSchema(field="app_name", operators=["eq", "like"])
app_platform_filter = AllowedFilterSchema(field="platform", operators=["eq", "like"])
app_is_active_filter = AllowedFilterSchema(field="is_active", operators=["eq"])
allowed_application_registration_filters = [
    app_name_filter,
    app_platform_filter,
    app_is_active_filter,
    created_at_filter,
    is_deleted_filter,
]

############################# application registration sorts ################################
app_name_sort = AllowedSortSchema(field="platform")
allowed_application_registration_sorts = [app_name_sort, created_at_sort, is_deleted_sort]


############################## application api key filters without joins ###########################
application_api_key_filters_without_joins = [
    "api_key_id",
    "application_id",
    "revoked",
    "revoked_reason",
    "created_at",
    "is_deleted",
    "deleted_at",
]

############################ allowed application api key filters ###################################
api_key_id_filter = AllowedFilterSchema(field="api_key_id", operators=["eq"])
application_id_filter = AllowedFilterSchema(field="application_id", operators=["eq"])
revoked_filter = AllowedFilterSchema(field="revoked", operators=["eq"])
revoked_reason_filter = AllowedFilterSchema(field="revoked_reason", operators=["eq"])
application_api_key_app_name_filter = AllowedFilterSchema(field="app_name", operators=["eq"])
allowed_application_api_key_filters = [
    api_key_id_filter,
    application_id_filter,
    revoked_filter,
    revoked_reason_filter,
    application_api_key_app_name_filter,
    created_at_filter,
    is_deleted_filter,
]

############################# application api key sorts ################################
revoked_reason_sort = AllowedSortSchema(field="revoked_reason")
allowed_application_api_key_sorts = [revoked_reason_sort, created_at_sort, is_deleted_sort]
