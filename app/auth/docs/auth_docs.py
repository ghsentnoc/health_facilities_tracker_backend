register_user_docs = """
### This endpoint is used for register a user.

The following permissions have the authority to register a user:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
- {\n
    email: string,\n
    password: string,\n
    role_ids: [string],\n
    user_profile: {\n
        first_name: string,\n
        last_name: string,\n
        phone_number: string,\n
        country: string,\n
        facility_id: Optional[string]\n
    }\n
}

### Response Body
- General response schema
"""
