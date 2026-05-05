submit_form_response_docs = """
### This endpoint is used to submit answers for a published form.

- Conditional logic is evaluated server-side: fields hidden by conditions are excluded from storage.
- Required visible fields that are missing will return a 422 error.

### Request Body:
{
    "form_id": "string",
    "submitted_by": "string (optional, user_id or facility_id)",
    "answers": {
        "field_id_1": "value",
        "field_id_2": "value",
        ...
    }
}

### Response Body
- General response schema
"""

get_all_responses_docs = """
### This endpoint is used for getting all form responses.

### Query Parameters:
- filters: Allowed filters: form_id (eq), submitted_by (eq), created_at (eq, ne, gt, lt, ge, le), is_deleted (eq)
- sort: Allowed sorts: submitted_at (asc, desc), created_at (asc, desc)
- pagination: Pagination settings.

### Response Body
- General response schema
"""

get_response_by_id_docs = """
### This endpoint is used for getting a single form response by id.

### Path Parameters:
- response_id {string}

### Response Body
- General response schema
"""

get_responses_for_form_docs = """
### This endpoint is used for getting all responses submitted for a specific form.

### Path Parameters:
- form_id {string}

### Response Body
- General response schema
"""

delete_response_docs = """
### This endpoint is used for soft-deleting a form response by id.

### Path Parameters:
- response_id {string}

### Response Body
- General response schema
"""
