# Task Manager API Contract (v1)

> **Curriculum Module**: Phase 1 (Days 1–10) — HTTP, REST, PostgreSQL, SQL and Django Foundations  
> **Core Concepts Covered in this Document**:
> 1. **Client-Server Architecture**: Request-Response Lifecycle & Statelessness
> 2. **REST Principles**: Resource-Oriented URI Design (Nouns vs. Verbs), Plural Collections
> 3. **HTTP Verb Semantics & Idempotency**: Safe (`GET`) vs. Idempotent (`PUT`, `DELETE`) vs. Non-Idempotent (`POST`, `PATCH`)
> 4. **Parameter Types**: Path (Identity), Query (Filter/Sort/Page), Body (Payload), Header (Metadata/Auth)
> 5. **HTTP Status Codes**: Semantic families (2xx Success, 4xx Client Fault, 5xx Server Fault)
> 6. **Standardized Error Handling**: Machine-readable error codes and structured validation envelopes
> 7. **API Versioning**: URI Path Versioning (`/api/v1/`) to prevent breaking client contracts

This document serves as the formal specification and contractual agreement between client applications (web, mobile, external consumers) and the Django REST backend.

---

## 1. Core Architectural Concepts & REST Conventions

### Concept 1.1: Client-Server Architecture & Statelessness
- The client and server are completely decoupled. The client cares only about presentation and user interaction; the server cares only about business logic, data persistence, and security.
- Every HTTP request must be **stateless**: the server does not rely on a persistent memory connection from prior requests. Each request carries all authentication credentials and metadata needed to be understood and fulfilled independently.

### Concept 1.2: Resource-Oriented URIs (Nouns, Not Verbs)
In REST, endpoints are modeled around **resources** (entities in the system), not remote procedure calls (RPC):
- ✅ `GET /api/v1/tasks/` — Retrieve a collection of task resources
- ❌ `GET /api/v1/getTasks` — Anti-pattern: Verb in the URI
- ✅ `POST /api/v1/tasks/` — Create a new task resource
- ❌ `POST /api/v1/tasks/create/` — Anti-pattern: Redundant action verb

### Concept 1.3: HTTP Methods, Idempotency & Safety
Understanding method safety and idempotency prevents data corruption and duplicate actions across unreliable networks:

| HTTP Method | Safe? (Read-Only) | Idempotent? (Repeatable) | Semantic Purpose in Task Manager |
| :--- | :---: | :---: | :--- |
| **`GET`** | **Yes** | **Yes** | Retrieve task or project representations without side effects |
| **`POST`** | No | **No** | Create a subordinate resource (e.g. creating a new task) |
| **`PUT`** | No | **Yes** | Replace an entire resource representation with new data |
| **`PATCH`** | No | **No / Conditional** | Partially update specific attributes (e.g. changing only status) |
| **`DELETE`** | No | **Yes** | Remove a resource; subsequent calls still leave it absent |

### Concept 1.4: Parameter Types & Their Exact Roles
1. **Path Parameters** (e.g. `/api/v1/tasks/{id}/`):
   - *Role*: Identify a specific unique resource instance.
2. **Query Parameters** (e.g. `/api/v1/tasks/?status=IN_PROGRESS&page=2`):
   - *Role*: Filter, search, paginate, or order collections without altering resource identity.
3. **Body Parameters** (e.g. JSON in request body):
   - *Role*: Provide the representation payload for creation or modification.
4. **Header Parameters** (e.g. `Authorization: Bearer <token>`, `X-Request-ID: <uuid>`):
   - *Role*: Carry cross-cutting metadata, authentication tokens, and tracing identifiers.

### Concept 1.5: HTTP Status Codes & Semantic Integrity
Status codes communicate outcome categories unambiguously:
- **`200 OK`**: Successful request returning a response body (reads, updates).
- **`201 Created`**: Successful creation; resource now exists on server.
- **`204 No Content`**: Successful operation with intentionally empty response body (typical for `DELETE`).
- **`400 Bad Request`**: Client payload failed validation or malformed JSON.
- **`401 Unauthorized`**: Authentication missing, expired, or invalid.
- **`403 Forbidden`**: Authenticated identity is forbidden from accessing/modifying the resource.
- **`404 Not Found`**: Target URI or resource ID does not exist.
- **`405 Method Not Allowed`**: Target endpoint does not accept the requested HTTP method.
- **`429 Too Many Requests`**: Rate limit exceeded by the client.
- **`500 Internal Server Error`**: Unexpected server-side bug or unhandled crash.

---

## 2. Error Response Architecture & Standard Envelopes

> **Concepts Covered**: Predictable Error Contracts, Machine-Readable Error Codes, Field-Level vs. Non-Field Errors.

Clients should never have to guess whether an error response contains a string, an array, or a dictionary. All 4xx and 5xx responses conform to a unified error schema:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The submitted data failed validation constraints.",
    "details": {
      "due_date": [
        "Due date cannot be set in the past."
      ],
      "title": [
        "This field is required."
      ],
      "non_field_errors": [
        "A task with this title already exists in this project."
      ]
    }
  }
}
```

- `code`: Machine-readable token (e.g., `VALIDATION_ERROR`, `PERMISSION_DENIED`, `NOT_FOUND`, `AUTHENTICATION_FAILED`) enabling client-side programmatic branching.
- `message`: Human-readable summary suitable for user feedback.
- `details`: Detailed map of field-specific errors, matching frontend form inputs.

---

## 3. Endpoints Specification & Concepts Mapping

### 3.1 Authentication Endpoints (`/api/v1/auth/`)

> **Concepts Covered**: Token-Based Authentication (JWT), Stateless Authentication, Access vs. Refresh Token Lifecycle.

#### `POST /api/v1/auth/token/`
- **Concept**: Credential exchange for short-lived access token and long-lived refresh token.
- **HTTP Method**: `POST` (credentials sent in encrypted HTTPS body, not in query string/URL).
- **Request Body**:
  ```json
  {
    "username": "rushi",
    "password": "SecretPassword123"
  }
  ```
- **Responses**:
  - `200 OK`:
    ```json
    {
      "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
  - `401 Unauthorized`:
    ```json
    {
      "error": {
        "code": "AUTHENTICATION_FAILED",
        "message": "No active account found with the given credentials.",
        "details": {}
      }
    }
    ```

#### `POST /api/v1/auth/token/refresh/`
- **Concept**: Silent token renewal without prompting the user to re-enter credentials.
- **Request Body**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Responses**:
  - `200 OK`: Returns refreshed access token.
  - `401 Unauthorized`: Refresh token expired or invalidated.

---

### 3.2 Projects Endpoints (`/api/v1/projects/`)

> **Concepts Covered**: Resource Collections, Sub-Resource Aggregation Endpoints (`/stats/`), Object Ownership Permissions.

#### `GET /api/v1/projects/`
- **Concept**: Paginated collection retrieval with text search and sort ordering.
- **Query Parameters**:
  - `page` (integer, default: `1`): Pagination page number.
  - `page_size` (integer, default: `20`, max: `100`): Results per page.
  - `search` (string): Text search across project name and description.
  - `ordering` (string): Order by field name (e.g. `created_at`, `-created_at`, `name`).
- **Response**: `200 OK`
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "Backend Curriculum",
        "description": "20-day intensive backend development plan",
        "owner": {
          "id": 1,
          "username": "rushi"
        },
        "task_count": 12,
        "created_at": "2026-10-21T07:00:00Z",
        "updated_at": "2026-10-21T07:15:00Z"
      }
    ]
  }
  ```

#### `POST /api/v1/projects/`
- **Concept**: Resource creation. The authenticated user is automatically assigned as the project owner.
- **Request Body**:
  ```json
  {
    "name": "E-Commerce Microservices",
    "description": "Payment and inventory services"
  }
  ```
- **Response**: `201 Created`

#### `GET /api/v1/projects/{id}/`
- **Concept**: Single resource retrieval by Path Parameter.
- **Responses**: `200 OK` or `404 Not Found`.

#### `PATCH /api/v1/projects/{id}/`
- **Concept**: Partial update. Omitting fields does not clear them.
- **Response**: `200 OK`.

#### `DELETE /api/v1/projects/{id}/`
- **Concept**: Idempotent resource removal. Only project owners are authorized.
- **Responses**: `204 No Content` (success) or `403 Forbidden` (non-owner).

#### `GET /api/v1/projects/{id}/stats/`
- **Concept**: Sub-resource aggregation endpoint. Returns calculated SQL metrics rather than raw rows.
- **Response**: `200 OK`
  ```json
  {
    "project_id": 1,
    "total_tasks": 15,
    "by_status": {
      "TODO": 5,
      "IN_PROGRESS": 7,
      "COMPLETED": 3
    },
    "by_priority": {
      "LOW": 2,
      "MEDIUM": 8,
      "HIGH": 5
    }
  }
  ```

---

### 3.3 Tasks Endpoints (`/api/v1/tasks/`)

> **Concepts Covered**: Relational Filtering (Foreign Key lookups), Status & Priority Enums, Partial Updates (`PATCH` vs. `PUT`).

#### `GET /api/v1/tasks/`
- **Concept**: Multi-criteria relational filtering and ordering.
- **Query Parameters**:
  - `project` (integer): Filter tasks belonging to a specific Project ID.
  - `status` (string enum): `TODO`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`.
  - `priority` (string enum): `LOW`, `MEDIUM`, `HIGH`, `URGENT`.
  - `assignee` (integer): Filter by assigned user ID.
  - `due_date_before` (date: `YYYY-MM-DD`): Tasks due on or before date.
  - `search` (string): Search title and description.
  - `ordering` (string): e.g., `due_date`, `-priority`, `-created_at`.
  - `page` (integer): Page number.
- **Response**: `200 OK`
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 101,
        "title": "Design PostgreSQL Schema",
        "description": "Normalize project and task entities to 3NF",
        "project": {
          "id": 1,
          "name": "Backend Curriculum"
        },
        "assignee": {
          "id": 1,
          "username": "rushi"
        },
        "creator": {
          "id": 1,
          "username": "rushi"
        },
        "status": "IN_PROGRESS",
        "priority": "HIGH",
        "due_date": "2026-10-25",
        "created_at": "2026-10-21T07:20:00Z",
        "updated_at": "2026-10-21T07:20:00Z"
      }
    ]
  }
  ```

#### `POST /api/v1/tasks/`
- **Concept**: Creation with relational foreign key validation (`project_id`, `assignee_id`).
- **Request Body**:
  ```json
  {
    "title": "Fix N+1 query issue",
    "description": "Add select_related to task list endpoint",
    "project_id": 1,
    "assignee_id": 1,
    "status": "TODO",
    "priority": "HIGH",
    "due_date": "2026-10-28"
  }
  ```
- **Responses**:
  - `201 Created`
  - `400 Bad Request` (Validation errors, e.g. due date in the past, invalid foreign key).

#### `GET /api/v1/tasks/{id}/`
- **Response**: `200 OK` or `404 Not Found`.

#### `PATCH /api/v1/tasks/{id}/`
- **Concept**: State mutation. Updating task status from `TODO` to `IN_PROGRESS` or reassigning task.
- **Request Body**:
  ```json
  {
    "status": "COMPLETED"
  }
  ```
- **Response**: `200 OK`.

#### `DELETE /api/v1/tasks/{id}/`
- **Response**: `204 No Content`.
