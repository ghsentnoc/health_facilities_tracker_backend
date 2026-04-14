from app.core.schemas.query_params_schemas import AllowedFilterSchema, AllowedSortSchema
from app.core.utils.allowed_filters_sort import created_at_filter, created_at_sort, is_deleted_filter, is_deleted_sort

#################################### filters without joins ##################################
region_filters_without_joins = ["name", "created_at", "is_deleted"]
district_filters_without_joins = region_filters_without_joins.copy() + ["region_id"]
facility_filters_without_joins = region_filters_without_joins.copy() + [
    "ownership",
    "facility_type",
    "registration_number",
    "is_approved",
    "is_licensed",
    "district_id",
]

#################################### filters with joins ######################################
district_filters_with_joins = ["region_name"]
facility_filters_with_joins = ["region_name", "district_name", "region_id"]


################################### allowed region filters ###################################
region_name_filter = AllowedFilterSchema(field="name", operators=["eq", "like"])
allowed_region_filters = [region_name_filter, created_at_filter, is_deleted_filter]

##################################### allowed region sorts ###################################
region_name_sort = AllowedSortSchema(field="name")
allowed_region_sorts = [region_name_sort, created_at_sort, is_deleted_sort]


#################################### allowed district filters ################################
district_name_filter = AllowedFilterSchema(field="name", operators=["eq", "like"])
district_region_id_filter = AllowedFilterSchema(field="region_id", operators=["eq"])
district_region_name_filter = AllowedFilterSchema(field="region_name", operators=["eq", "like"])
allowed_district_filters = [
    district_name_filter,
    district_region_id_filter,
    district_region_name_filter,
    created_at_filter,
    is_deleted_filter,
]

######################### allowed district sorts #############################################
district_name_sort = AllowedSortSchema(field="name")
district_region_name_sort = AllowedSortSchema(field="region_name")
allowed_district_sorts = [district_name_sort, district_region_name_sort, created_at_sort, is_deleted_sort]


######################## allowed facility filters ###########################################
facility_name_filter = AllowedFilterSchema(field="name", operators=["eq", "like"])
facility_district_name_filter = AllowedFilterSchema(field="district_name", operators=["eq", "like"])
facility_district_id_filter = AllowedFilterSchema(field="district_id", operators=["eq"])
facility_region_name_filter = AllowedFilterSchema(field="region_name", operators=["eq", "like"])
facility_region_id_filter = AllowedFilterSchema(field="region_id", operators=["eq"])
facility_ownership_filter = AllowedFilterSchema(field="ownership", operators=["eq", "like"])
facility_type_filter = AllowedFilterSchema(field="facility_type", operators=["eq", "like"])
facility_is_approved_filter = AllowedFilterSchema(field="is_approved", operators=["eq"])
facility_is_licensed_filter = AllowedFilterSchema(field="is_licensed", operators=["eq"])
allowed_facility_filters = [
    facility_name_filter,
    facility_district_name_filter,
    facility_district_id_filter,
    facility_region_name_filter,
    facility_region_id_filter,
    facility_type_filter,
    facility_ownership_filter,
    facility_is_approved_filter,
    facility_is_licensed_filter,
    created_at_filter,
    is_deleted_filter,
]

######################### allowed facility sorts ################################################
facility_name_sort = AllowedSortSchema(field="name")
facility_district_name_sort = AllowedSortSchema(field="district_name")
facility_region_name_sort = AllowedSortSchema(field="region_name")
allowed_facility_sorts = [
    facility_name_sort,
    facility_district_name_sort,
    facility_region_name_sort,
    created_at_sort,
    is_deleted_sort,
]
