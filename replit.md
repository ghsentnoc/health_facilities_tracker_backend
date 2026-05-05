# Health Facilities Tracker — Backend API

## Overview
A FastAPI backend for tracking healthcare facilities and their services (cervical/breast cancer care). Provides tools for data collection, auditing, and reporting.

## Stack
- **Language**: Python 3.10+
- **Framework**: FastAPI (served via Uvicorn/Gunicorn)
- **Database**: MySQL (SQLAlchemy ORM + Alembic migrations)
- **Cache**: Redis
- **Auth**: JWT-based + API key validation
- **Email**: FastAPI-Mail (Jinja2 templates)
- **Validation**: Pydantic v2

## Project Structure
```
app/
├── main.py               # FastAPI app + router registration
├── database/             # SQLAlchemy Base + session setup
├── core/                 # Config, base classes, shared utils
│   ├── config/           # DB, mail, Redis, project config
│   ├── dependencies/     # DB session dependency
│   ├── factories/        # Base repository/service factories
│   ├── handlers/         # Exception handlers
│   ├── mixins/           # IdentityMixin, AuditMixin, SoftDeleteMixin
│   ├── models/           # associations + wildcard model imports
│   ├── repositories/     # BaseReadRepository, BaseWriteRepository
│   ├── schemas/          # BaseReadSchema, ResponseSchema, query params
│   ├── services/         # BaseService
│   └── utils/            # constants, messages, validators, general
├── auth/                 # JWT auth, roles, permissions, API keys
├── users/                # User CRUD, profiles, facility associations
├── locations/            # Regions, districts, facilities
└── forms/                # Dynamic form system (see below)
```

## Module Conventions
Each feature module (auth, users, locations, forms) follows the same layered structure:
- `models/` — SQLAlchemy models using mixins (IdentityMixin, AuditCreateMixin, AuditUpdateMixin, SoftDeleteMixin)
- `schemas/request/` — Pydantic request schemas
- `schemas/response/` — Pydantic response schemas (extend BaseReadSchema)
- `repositories/` — Extend BaseReadRepository + BaseWriteRepository
- `services/` — Extend BaseService; contain all business logic
- `factories/` — Repository and service factories
- `dependencies/` — FastAPI Depends() functions to inject services
- `routes/api/v1/` — APIRouter endpoints
- `docs/` — Docstring constants for route descriptions
- `utils/constants.py` — Enums for the module
- `utils/allowed_filters_sort.py` — Filter/sort configuration

## API Endpoints
All routes are mounted under `/api/v1/`.
- API docs: `GET /api/documentation` (Swagger UI)
- ReDoc: `GET /api/redoc`

### Auth & Users
- `POST /auth/login`, `POST /auth/logout`, `POST /auth/refresh`
- `GET/POST/PUT/DELETE /users`
- `GET/POST/PUT /roles`, `GET/POST/PUT /permissions`

### Locations
- `GET/POST/PUT/DELETE /regions`
- `GET/POST/PUT/DELETE /districts`
- `GET/POST/PUT/DELETE /facilities`

### Forms (Dynamic Form System)
- `POST /forms` — Create a form (with optional nested sections + fields)
- `GET /forms` — List all forms (filterable, sortable, paginated)
- `GET /forms/{form_id}` — Get full form schema (sections + fields)
- `PUT /forms/{form_id}` — Update form metadata
- `DELETE /forms/{form_id}` — Soft-delete a form
- `PATCH /forms/{form_id}/restore` — Restore a deleted form
- `POST /forms/{form_id}/sections` — Add a section to a form
- `GET /forms/{form_id}/sections` — List all sections for a form
- `PUT /forms/sections/{section_id}` — Update a section
- `DELETE /forms/sections/{section_id}` — Soft-delete a section
- `POST /forms/sections/{section_id}/fields` — Add a field to a section
- `GET /forms/sections/{section_id}/fields` — List fields in a section
- `PUT /forms/fields/{field_id}` — Update a field
- `DELETE /forms/fields/{field_id}` — Soft-delete a field
- `POST /form-responses` — Submit answers to a published form
- `GET /form-responses` — List all responses
- `GET /form-responses/{response_id}` — Get a single response
- `GET /form-responses/form/{form_id}` — All responses for a form
- `DELETE /form-responses/{response_id}` — Soft-delete a response

## Forms Module — Key Design Decisions
- **Form status**: `draft` | `published` | `archived` — only published forms accept submissions.
- **Field types**: `text`, `number`, `textarea`, `select`, `multiselect`, `checkbox`, `radio`, `date`
- **Conditional logic**: Each field can have `conditional_logic: { depends_on_field: "<field_id>", show_if: "<value>" }`. On submission, the server evaluates all conditions, strips hidden-field answers, and validates required visible fields.
- **JSON columns**: `options`, `validation`, `conditional_logic`, and `answers` are stored as JSON in MySQL.
- **Soft deletes**: All entities use `is_deleted` + `deleted_at` fields; relationships filter out deleted children via `primaryjoin` conditions.
- **Alembic migration**: `db_migrations/versions/a1b2c3d4e5f6_add_dynamic_form_system.py` creates the four new tables (`forms`, `form_sections`, `form_fields`, `form_responses`).

## Environment Variables
See `.env.example`. Required:
- `DB_*` — MySQL connection settings per environment (DEV/TEST/PROD)
- `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRES_IN_MINUTES`, `REFRESH_TOKEN_EXPIRES_IN_MINUTES`
- `MAIL_*` — SMTP settings
- `REDIS_*` — Redis connection settings
- `PROJECT_ENV` — `DEV` | `TEST` | `PROD`
- `PROJECT_PLATFORM` — `Local` | `Docker`

## Running
```bash
# Apply migrations
./run_alembic_upgrade.sh

# Start with Uvicorn (dev)
./run_app_with_uvicorn.sh
```
