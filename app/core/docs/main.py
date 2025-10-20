project_description = """
The {app_name} is a web platform that helps monitor and analyze healthcare services across facilities. 
It tracks facilities offering cervical cancer, breast cancer, maternal, and perinatal care services, 
providing tools for data collection, auditing, and reporting. 
The goal is to drive data-informed decisions and improve health outcomes through better visibility and accountability 
in healthcare delivery.

This API powers the core functionalities of the Health Facilities Tracker, including:

- Secure user and role-based access management
- Data entry and retrieval of maternal and perinatal cases
- Audit workflows and review processes
- Reporting and visualization of key indicators
- Decision support for improving maternal and newborn health outcomes

The system is built with FastAPI to ensure high performance, scalability, and ease of integration with other
health information systems.

## Query Parameters

### Filters

- Format: JSON
- Example: {{"field": {{"value": "any_value", "operator": "eq"}}}}
- value: any valid JSON type
- operator: optional, one of ["eq", "gt", "ge", "lt", "le", "ne", "like"]

#### Sort

- Format: JSON
- Example: {{"field": "asc"}}
- mode: can be "asc" or "desc"

#### Pagination

- Format: JSON
- Example: {{"page": 1, "page_size": 20}}
- Keys: page and page_size only
##### Defaults:
- If page or page_size is null, defaults are applied
- If one is provided, the other falls to default
- If values are not integers or less than 1, defaults to 1

## General Response Schema
{{\n
  "status": "string",       // "success" or "error"\n
  "status_code": 100,       // integer between 100 and 599\n
  "message": "string",      // description of result\n
  "data": [ "string" ],     // can be null\n
  "extras": {{}}              // optional metadata, can be null\n
}}
"""
