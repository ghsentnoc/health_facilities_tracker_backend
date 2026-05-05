create_form_docs = """
### This endpoint is used to create a new form.

Optionally include sections (with fields) to create the full form structure in one request.

### Request Body:
{
    "title": "string",
    "description": "string (optional)",
    "status": "draft | published | archived",
    "sections": [
        {
            "title": "string (optional)",
            "description": "string (optional)",
            "order": 0,
            "fields": [
                {
                    "label": "string",
                    "field_type": "text | number | textarea | select | multiselect | checkbox | radio | date",
                    "required": false,
                    "placeholder": "string (optional)",
                    "options": ["string"] (optional),
                    "validation": { 
                    "min_length": int, "max_length": int, "min": float, "max": float, "regex": "string" } (optional),
                    "default_value": "string (optional)",
                    "order": 0,
                    "conditional_logic": { "depends_on_field": "field_id", "show_if": "value" } (optional),
                    "help_text": "string (optional)"
                }
            ]
        }
    ]
}

### Response Body
- General response schema
"""

get_all_forms_docs = """
### This endpoint is used for getting all forms.

### Query Parameters:
- filters: A JSON string representing the filters to apply.
    - Allowed filters: title (eq, like), status (eq), 
    created_by (eq), created_at (eq, ne, gt, lt, ge, le), is_deleted (eq)
- sort: A JSON string representing the sort order.
    - Allowed sorts: title (asc, desc), status (asc, desc), created_at (asc, desc)
- pagination: A JSON string representing the pagination settings.

### Response Body
- General response schema
"""

get_form_by_id_docs = """
### This endpoint is used for getting a form by id (includes full schema: sections and fields).

### Path Parameters:
- form_id {string}

### Response Body
- General response schema
"""

update_form_docs = """
### This endpoint is used for updating a form's metadata (title, description, status).

### Path Parameters:
- form_id {string}

### Request Body:
{
    "title": "string (optional)",
    "description": "string (optional)",
    "status": "draft | published | archived (optional)"
}

### Response Body
- General response schema
"""

delete_form_docs = """
### This endpoint is used for soft-deleting a form by id.

### Path Parameters:
- form_id {string}

### Response Body
- General response schema
"""

restore_form_docs = """
### This endpoint is used for restoring a soft-deleted form by id.

### Path Parameters:
- form_id {string}

### Response Body
- General response schema
"""

create_section_docs = """
### This endpoint is used to add a new section to an existing form.

### Path Parameters:
- form_id {string}

### Request Body:
{
    "title": "string (optional)",
    "description": "string (optional)",
    "order": 0,
    "fields": [ ... ] (optional)
}

### Response Body
- General response schema
"""

get_sections_docs = """
### This endpoint is used for getting all sections for a form.

### Path Parameters:
- form_id {string}

### Response Body
- General response schema
"""

update_section_docs = """
### This endpoint is used for updating a form section.

### Path Parameters:
- section_id {string}

### Request Body:
{
    "title": "string (optional)",
    "description": "string (optional)",
    "order": int (optional)
}

### Response Body
- General response schema
"""

delete_section_docs = """
### This endpoint is used for soft-deleting a form section.

### Path Parameters:
- section_id {string}

### Response Body
- General response schema
"""

create_field_docs = """
### This endpoint is used to add a new field to a section.

### Path Parameters:
- section_id {string}

### Request Body:
{
    "label": "string",
    "field_type": "text | number | textarea | select | multiselect | checkbox | radio | date",
    "required": false,
    "placeholder": "string (optional)",
    "options": ["string"] (optional),
    "validation": { ... } (optional),
    "default_value": "string (optional)",
    "order": 0,
    "conditional_logic": { "depends_on_field": "field_id", "show_if": "value" } (optional),
    "help_text": "string (optional)"
}

### Response Body
- General response schema
"""

get_fields_docs = """
### This endpoint is used for getting all fields within a section.

### Path Parameters:
- section_id {string}

### Response Body
- General response schema
"""

update_field_docs = """
### This endpoint is used for updating a form field.

### Path Parameters:
- field_id {string}

### Response Body
- General response schema
"""

delete_field_docs = """
### This endpoint is used for soft-deleting a form field.

### Path Parameters:
- field_id {string}

### Response Body
- General response schema
"""
