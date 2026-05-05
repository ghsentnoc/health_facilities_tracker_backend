You are working inside an existing Python backend project. The framework, database, and libraries are already set up. Follow the existing conventions and structure, using **snake_case** for variable names and field names.

Do NOT suggest or introduce new frameworks, libraries, or databases. Follow the exact project structure and conventions in place.

---

## TASK: Implement a Dynamic Form System with Sections, Fields, Conditional Logic, and Answers Storage

### Objective
We need to implement a **dynamic form system** where:
- Forms have a **description**.
- Forms consist of **sections** that contain multiple fields.
- Each field can have **validation**, **default values**, and **conditional logic**.
- Form **answers** should be stored by users when they submit the form, and responses should be tied to the corresponding **form**, **sections**, and **fields**.
- The backend must handle **form creation**, **form schema generation**, **field validation**, **conditional logic processing**, and **response storage**.
- Forms must also support **conditional logic** (i.e., fields shown/hidden based on previous field answers).

### BACKEND REQUIREMENTS

#### 1. **Form Schema (Model)**

The form schema should store the form's metadata, description, sections, and the fields within each section.

The **form model** should include:

- **id**: Unique form ID
- **title**: Form title
- **description**: Detailed description of the form
- **created_by**: Admin who created the form (use a user reference if applicable)
- **created_at**: Timestamp of form creation
- **updated_at**: Timestamp of last update
- **status**: Enum (`draft`, `published`, `archived`)
- **sections**: Array of sections (defined below)

#### 2. **Sections (Model)**

Each form will consist of one or more **sections**. Each section will contain a list of fields.

Each **section** should include:

- **id**: Unique section ID
- **title**: Section title (optional)
- **description**: Section description (optional)
- **fields**: List of field IDs that belong to this section (array)

#### 3. **Field Schema (Integrated with Conditional Logic)**

Each field within the form should have the following attributes:

- **id**: Unique field ID
- **label**: Display label for the field
- **type**: Type of input field (e.g., text, number, textarea, select, multiselect, checkbox, radio, date)
- **required**: Boolean indicating if the field is required
- **placeholder**: Optional placeholder for input
- **options**: Options for fields like `select`, `multiselect`, `radio`, and `checkbox`
- **validation**: Validation rules, such as:
  - **min_length**, **max_length**
  - **min**, **max**
  - **regex** (for custom validation patterns)
- **default_value**: Default value for the field
- **order**: Position of the field in the section
- **conditional_logic**: Logic to determine if the field should be shown or hidden based on other field values. It will include:
  - **depends_on_field**: The field ID which drives the condition
  - **show_if**: The value that will make the field visible
- **help_text**: Optional guidance for the user (e.g., tooltip)

#### 4. **Response Model (Store User Submissions)**

When a user submits a form, the responses will be stored in the **response model**, which links the answers to the form, sections, and fields.

Each **response model** should include:

- **id**: Unique submission ID
- **form_id**: Reference to the form being filled
- **user_id** (or facility_id): Reference to the user or facility submitting the form
- **answers**: JSON object where keys are field IDs and values are the corresponding answers from the user
- **submitted_at**: Timestamp of submission

Example of **answers** stored as JSON:

```json
{
  "field_1": "Yes",
  "field_2": "5",
  "field_3": "2022-01-01"
}