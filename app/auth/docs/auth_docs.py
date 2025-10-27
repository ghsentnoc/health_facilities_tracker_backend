register_user_docs = """
### This endpoint is used for register a user.

The following permissions have the authority to register a user:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{\n
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

verify_account_docs = """
### This endpoint is used for verifying an account.

The following permissions have the authority to verify an account:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{\n
    token: string\n
}

### Response Body
- General response schema
"""

resend_account_verification_link_docs = """
### This endpoint is used for resending an account verification link.

The following permissions have the authority to resend the account verification link.:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{\n
    email: string\n
}

### Response Body
- General response schema
"""

request_password_reset_docs = """
### This endpoint is used for requesting a password reset.

The following permissions have the authority to request a password reset.:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{\n
    email: string\n
}

### Response Body
- General response schema
"""

verify_password_reset_token_docs = """
### This endpoint is used for verifying a password reset token.

The following permissions have the authority to verify a password reset token.:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{\n
    token: string\n
}

### Response Body
- General response schema
"""

reset_password_docs = """
### This endpoint is used for resetting a password.

The following permissions have the authority to reset password.:

- `all`

### Path Parameters:
- None

### Query Parameters:
- None

### Request Body:
{\n
    email: string,\n
    password: string,\n
    token: string\n
}

### Response Body
- General response schema
"""
