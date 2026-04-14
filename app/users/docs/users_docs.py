register_admin_docs = """
### This endpoint is used for registering an admin.

This flow is additive and does not replace the existing user endpoints.

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{
    email: string,
    role_ids: [string],
    user_profile: {
        first_name: string,
        last_name: string,
        phone_number: string,
        country: string
    }
}

### Response Body
- General response schema
"""

register_facility_representative_docs = """
### This endpoint is used for registering a facility representative.

This keeps the existing self-service registration flow.

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{
    email: string,
    password: string,
    user_profile: {
        first_name: string,
        last_name: string,
        phone_number: string,
        country: string
    },
    facility_info: {
        facility_id: string
    }
}

### Response Body
- General response schema
"""

register_facility_representative_by_admin_docs = """
### This endpoint is used for registering a facility representative by an admin.

This is added alongside the existing registration flow so you can keep the current one.

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{
    email: string,
    user_profile: {
        first_name: string,
        last_name: string,
        phone_number: string,
        country: string
    },
    facility_info: {
        facility_id: string
    }
}

### Response Body
- General response schema
"""

get_all_users_docs = """
### This endpoint is used for getting all users.

The following users have the authority to get all users:

- `Super Administrator`

### Path Parameters:
- None

### Query Parameters:
- filters:  A JSON string representing the filters to apply.
    - Allowed filters and operators:
        - name: eq, like
        - created_at: eq, ne, gt, lt, ge, le
        - is_deleted: eq
- sort: A JSON string representing the sort order.
    - Allowed sorts:
        - name: asc, desc
- pagination: A JSON string representing the pagination settings.

### Request Body:
- None

### Response Body
- General response schema
"""

get_user_by_id_docs = """
### This endpoint is used for getting a user by id.

The following users have the authority to get all users:

- `Super Administrator`

### Path Parameters:
- user_id {string}

### Query Parameters:
- Filters
- None

### Request Body:
- None

### Response Body
- General response schema
"""

update_user_docs = """
### This endpoint is used for updating a user by id.

The following users have the authority to get all users:

- `Super Administrator`

### Path Parameters:
- user_id {string}

### Query Parameters:
- None

### Request Body:
{\n
    first_name: string,\n
    last_name: string,\n
    phone_number: string,\n
    country: string,\n
    facility_id: Optional[string]\n
}

### Response Body
- General response schema
"""

delete_user_docs = """
### This endpoint is used for deleting a user by id.

The following users have the authority to get all users:

- `Super Administrator`

### Path Parameters:
- user_id {string}

### Query Parameters:
- None

### Request Body:
- None

### Response Body
- General response schema
"""

restore_user_docs = """
### This endpoint is used for restoring a user by id.

The following users have the authority to get all users:

- `Super Administrator`

### Path Parameters:
- user_id {string}

### Query Parameters:
- None

### Request Body:
- None

### Response Body
- General response schema
"""

update_admin_docs = """
### This endpoint is used for updating an admin user by id.

### Path Parameters:
- user_id {string}

### Query Parameters:
- None

### Request Body:
{
    email: Optional[string],
    user_profile: Optional[{
        first_name: string,
        last_name: string,
        phone_number: string,
        country: string
    }]
}

### Response Body
- General response schema
"""

update_facility_representative_docs = """
### This endpoint is used for updating a facility representative user by id.

### Path Parameters:
- user_id {string}

### Query Parameters:
- None

### Request Body:
{
    email: Optional[string],
    user_profile: Optional[{
        first_name: string,
        last_name: string,
        phone_number: string,
        country: string
    }],
    facility_info: Optional[{
        facility_id: string
    }]
}

### Response Body
- General response schema
"""
