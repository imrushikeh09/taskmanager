# Task Manager API Contract (v1)

This document serves as the formal specification (API contract) between the frontend/client and the Django REST backend.

---

## 1. REST Architecture Principles & Conventions

1. **Resource-Oriented URIs (Nouns, Not Verbs)**:
   - ✅ `GET /api/v1/tasks/` (retrieve list of tasks)
   - ❌ `GET /api/v1/getTasks` or `POST /api/v1/tasks/create/`
2. **Plural Resource Nouns**:
   - `/api/v1/projects/`, `/api/v1/tasks/`, `/api/v1/users/`
3. **HTTP Verb Semantics**:
   - `GET`: Safe & Idempotent. Retrieve resources without side effects.
   - `POST`: Non-Idempotent. Create a new subordinate resource.
   - `PUT`: Idempotent. Replace the entire resource representation.
   - `PATCH`: Non-Idempotent (or conditionally idempotent). Partially modify specified fields.
   - `DELETE`: Idempotent. Remove the resource.
4. **Parameter Types**:
   - **Path parameters**: Identify a specific resource (e.g., `/api/v1/tasks/{id}/`).
   - **Query parameters**: Filter, paginate, search, or sort collections (e.g., `?status=IN_PROGRESS&page=2`).
   - **Body parameters**: Resource payloads sent in JSON format (`Content-Type: application/json`).
5. **Standard HTTP Status Codes**:
   - `200 OK`: Successful retrieval or update returning content.
   - `201 Created`: Resource successfully created. Returns `Location` header or created object.
   - `204 No Content`: Successful request with no response body (commonly `DELETE`).
   - `400 Bad Request`: Validation failure or malformed payload.
   - `401 Unauthorized`: Authentication missing or invalid (client identity unknown).
   - `403 Forbidden`: Authenticated user lacks permission for this action/resource.
   - `404 Not Found`: Resource does not exist.
   - `405 Method Not Allowed`: HTTP method not supported on this endpoint.
   - `429 Too Many Requests`: Rate limit / throttle exceeded.
   - `500 Internal Server Error`: Unhandled backend exception.

---

## 2. Standard Error Envelope

All 4xx and 5xx responses follow a consistent, predictable structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid field values provided.",
    "details": {
      "due_date": ["Due date cannot be in the past."],
      "title": ["This field is required."]
    }
  }
}
```

---

## 3. Endpoints Specification

### 3.1 Authentication (`/api/v1/auth/`)

#### `POST /api/v1/auth/token/`
- **Description**: Authenticate with credentials and receive JWT access and refresh tokens.
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
  - `401 Unauthorized`: Invalid credentials.

#### `POST /api/v1/auth/token/refresh/`
- **Description**: Obtain a fresh access token using a valid refresh token.
- **Request Body**:
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Responses**:
  - `200 OK`: Returns new access token.
  - `401 Unauthorized`: Expired or blacklisted refresh token.

---

### 3.2 Projects (`/api/v1/projects/`)

#### `GET /api/v1/projects/`
- **Description**: List projects accessible to the authenticated user.
- **Query Parameters**:
  - `page` (integer, default `1`): Page number.
  - `page_size` (integer, default `20`, max `100`): Results per page.
  - `search` (string): Search by name or description.
  - `ordering` (string): Sort field (e.g. `created_at`, `-created_at`, `name`).
- **Response**: `200 OK`
  ```json
  {
    "count": 2,
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
- **Description**: Create a new project.
- **Request Body**:
  ```json
  {
    "name": "E-Commerce Microservices",
    "description": "Payment and inventory services"
  }
  ```
- **Response**: `201 Created`

#### `GET /api/v1/projects/{id}/`
- **Description**: Retrieve detailed project information.
- **Responses**: `200 OK` or `404 Not Found`.

#### `PATCH /api/v1/projects/{id}/`
- **Description**: Partial update of project fields.
- **Response**: `200 OK`.

#### `DELETE /api/v1/projects/{id}/`
- **Description**: Delete a project (only allowed for project owner).
- **Response**: `204 No Content`.

#### `GET /api/v1/projects/{id}/stats/`
- **Description**: Aggregated task counts by status for a project.
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

### 3.3 Tasks (`/api/v1/tasks/`)

#### `GET /api/v1/tasks/`
- **Description**: Filter, search, and paginate tasks.
- **Query Parameters**:
  - `project` (integer): Filter by project ID.
  - `status` (string): `TODO`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`.
  - `priority` (string): `LOW`, `MEDIUM`, `HIGH`, `URGENT`.
  - `assignee` (integer): Filter by assigned user ID.
  - `due_date_before` (date: `YYYY-MM-DD`): Tasks due on or before date.
  - `search` (string): Search in `title` and `description`.
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
- **Description**: Create a task within a project.
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
  - `400 Bad Request` (Validation errors, e.g., due date in past or non-existent project).

#### `GET /api/v1/tasks/{id}/`
- **Response**: `200 OK` or `404 Not Found`.

#### `PATCH /api/v1/tasks/{id}/`
- **Description**: Update task status, priority, or assignee.
- **Request Body**:
  ```json
  {
    "status": "COMPLETED"
  }
  ```
- **Response**: `200 OK`.

#### `DELETE /api/v1/tasks/{id}/`
- **Response**: `204 No Content`.
