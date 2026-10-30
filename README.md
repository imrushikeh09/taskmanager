# TaskManager - Enterprise Full-Stack System

A production-grade, full-stack Task & Project Management application designed with an asynchronous **Django REST Framework** backend and a high-performance **React 18 + Vite** Single Page Application (SPA).

Built with modern software engineering practices: JWT authentication, Role-Based Access Control (RBAC), Celery task queues, Redis caching, visual SVG analytics, and a dual-theme modern SaaS design system.

---

## Architecture Overview

```
                      ┌───────────────────────────────────────┐
                      │          Client Web Browser           │
                      │  React 18 SPA (Vite / React Router)   │
                      └──────────────────┬────────────────────┘
                                         │  HTTP / REST (JWT)
                                         ▼
                      ┌───────────────────────────────────────┐
                      │          Nginx Reverse Proxy          │
                      │          Port 80 / Gateway            │
                      └──────────────────┬────────────────────┘
                                         │  Proxy /api/ & /media/
                                         ▼
                      ┌───────────────────────────────────────┐
                      │      Django REST Framework API        │
                      │   Gunicorn WSGI / Application Server  │
                      └───────┬──────────────┬──────────────┬─┘
                              │              │              │
                     Database │       Broker │        Cache │
                              ▼              ▼              ▼
                     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                     │  PostgreSQL  │ │ Redis Broker │ │ Redis Cache  │
                     └──────────────┘ └──────┬───────┘ └──────────────┘
                                             │
                                             ▼
                                     ┌──────────────┐
                                     │ Celery Worker│
                                     │ Async Tasks  │
                                     └──────────────┘
```

---

## Core Features

### 1. Frontend Experience (React 18 & Modern SaaS UI)
* **Visual Analytics & Donut Charts**: Interactive SVG status donut chart (Total Tasks & % Done), priority distribution bars, and project progress metrics.
* **Kanban Workflow Board**: 4-stage lifecycle board (`TODO`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`) with 1-click status transitions and quick-task creation.
* **Dual Design System**: Default **Warm Linen / Cream** theme (`#fbfbfa`) with high contrast readability, plus an instant toggle for refined **Dark Mode** (`#090a0f`), persisted in `localStorage`.
* **Enterprise Data Tables**: Search, multi-relational filters (status, priority, project, assignee), and pagination.
* **File Attachments**: Drag-and-drop file upload zone supporting documents & images up to 10MB.
* **In-App Notifications**: Real-time polling badge, dropdown preview, and full notification center.

### 2. Backend & API (Django REST Framework)
* **JWT Authentication & Silent Refresh**: Automatic access token injection (`Bearer <token>`) and silent refresh token rotation (`POST /api/v1/auth/token/refresh/`).
* **RBAC Authorization**: Granular permissions for `ADMIN`, `CONTRIBUTOR`, and `VIEWER` roles across projects, tasks, and attachments.
* **Asynchronous Jobs (Celery + Redis)**: Background email notifications and idempotency-backed assignment dispatchers.
* **Redis Cache-Aside**: High-speed caching for performance reports and project aggregation statistics.
* **Standardized Error Envelopes**: RFC-compliant error structures with field-level validation feedback.

---

## Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, React Router DOM v6, Context API, Pure CSS Design System (Zero UI Bloat) |
| **Backend** | Python 3.12, Django 5.x, Django REST Framework, SimpleJWT, Celery |
| **Database & Cache**| PostgreSQL 16 (or SQLite for quick local dev), Redis 7 |
| **DevOps & Infra** | Docker, Docker Compose, Nginx, Gunicorn, GitHub Actions CI / GitLab CI |

---

## Getting Started

### Option 1: Docker Compose (Recommended)

Run the full multi-container production stack (Postgres, Redis, Django Web, Celery Worker, Nginx):

```bash
# 1. Clone the repository
git clone https://github.com/imrushikeh09/taskmanager.git
cd taskmanager

# 2. Configure environment
cp .env.docker.example .env.docker

# 3. Build and launch containers
docker compose up -d --build

# 4. Apply migrations & seed demo enterprise data
docker compose exec web python manage.py migrate
docker compose exec web python scripts/seed_enterprise_data.py
```

* Frontend & API Gateway: `http://localhost:80`
* Swagger API Docs: `http://localhost:80/api/schema/swagger-ui/`

---

### Option 2: Local Development Setup

#### 1. Backend (Django REST Framework)

```bash
# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (defaults to SQLite if PostgreSQL is not active)
python manage.py migrate

# Seed sample projects, tasks, and users
python scripts/seed_enterprise_data.py

# Start Django development server
python manage.py runserver 8000
```

#### 2. Frontend (React 18 + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server with proxy to backend
npm run dev
```

Visit `http://localhost:5173` in your browser.

---

## Demo Accounts

When seeded with `scripts/seed_enterprise_data.py`, use any of the following accounts:

| Role | Username | Password | Access Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `Admin123!` | Full control: create, edit, delete tasks/projects, manage attachments. |
| **Contributor** | `sarah.chen` | `Contributor123!` | Create & edit assigned tasks, upload attachments, change statuses. |
| **Viewer** | `guest.viewer` | `Viewer123!` | Read-only access across all workspace dashboards and projects. |

---

## Project Structure

```
taskmanager/
├── accounts/                 # Custom User model & RBAC permissions
├── attachments/              # Multipart file upload API & storage
├── common/                   # Global middleware, exceptions & logging
├── config/                   # Django settings (base, dev, prod, testing)
├── notifications/            # In-app notifications & Celery dispatchers
├── projects/                 # Project workspaces & performance stats
├── tasks/                    # Task CRUD, filters, and lifecycle management
├── scripts/                  # Data seeding & migration utilities
├── nginx/                    # Reverse proxy & gateway configurations
├── docker-compose.yml        # Multi-container orchestration
│
└── frontend/                 # React 18 Single Page Application
    ├── src/
    │   ├── api/              # Modular HTTP client & endpoint services
    │   ├── components/       # Common icons, badges, modals, and tables
    │   │   ├── analytics/    # SVG Status Donut Chart & Urgency Meters
    │   │   ├── common/       # Navbar, StatusBadge, PriorityBadge, Icons
    │   │   ├── tasks/        # TaskTable, TaskCard, TaskAttachments
    │   │   └── projects/     # ProjectCard, ProjectStatsCard
    │   ├── context/          # AuthContext, NotificationContext, ThemeContext
    │   ├── pages/            # Dashboard, Tasks, Board, Projects, Details
    │   └── index.css         # Modern Warm Linen & Dark Theme CSS
    ├── package.json
    └── vite.config.js
```

---

## Testing & Quality Assurance

Run the comprehensive Django backend test suite:

```bash
python manage.py test --settings=config.settings.testing
```
*All 79 unit and integration tests covering JWT auth, RBAC permissions, Celery tasks, and file uploads pass with 100% success rate.*

---

## License

This project is open-source and available under the [MIT License](LICENSE).

