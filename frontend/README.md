# Task Manager Pro - Enterprise React Frontend

Modern, production-grade Single Page Application (SPA) built with React 18, Vite, and React Router DOM v6, communicating directly with the Django REST Framework backend.

---

## 1. Architectural Highlights

- **JWT Token Authentication & Silent Renewal**: Automatic Bearer token header injection and 401 Unauthorized handling with silent refresh token rotation (`POST /api/v1/auth/token/refresh/`).
- **RBAC Role-Based Access Control**: Fully hydrated user session (`GET /api/v1/auth/me/`) respecting `ADMIN`, `CONTRIBUTOR`, and `VIEWER` permission boundaries.
- **REST Resource Management**:
  - **Projects**: Directory, creation, updates, deletions, sub-resource SQL aggregation stats (`/stats/`), and Redis cache-aside performance reports (`/performance-report/`).
  - **Tasks**: Paginated directory, multi-parameter relational filtering (status, priority, project, assignee, dates), full-text search, ordering, and quick lifecycle state transitions.
  - **Kanban Board**: 4-column drag/click workflow view (`TODO`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`).
  - **Task Detail & File Attachments**: Multipart file upload manager supporting documents and images up to 10MB, uploader tracking, and instant download/delete.
  - **In-App Notifications**: Real-time unread bell indicator, notification dropdown, and dedicated notification center with batch read acknowledgment.
- **Standardized Error Handling**: Deep integration with backend RFC-compliant error envelopes (`error.code`, `error.message`, and field-level validation errors).

---

## 2. Directory Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.js                    # Dev server with /api and /media reverse proxy
└── src/
    ├── main.jsx                      # Application entry point
    ├── App.jsx                       # Router and ProtectedRoute declarations
    ├── index.css                     # Enterprise Dark UI design system
    ├── api/
    │   ├── client.js                 # Central HTTP client, interceptors, refresh queue
    │   ├── auth.js                   # Token exchange and profile hydration
    │   ├── projects.js               # Projects CRUD, metrics & cache-aside reports
    │   ├── tasks.js                  # Tasks CRUD, query filtering & ordering
    │   ├── attachments.js           # Multipart file uploads and deletion
    │   └── notifications.js         # In-app alerts and read acknowledgments
    ├── context/
    │   ├── AuthContext.jsx           # User identity, tokens, RBAC permission helpers
    │   └── NotificationContext.jsx   # Unread badge tracking and live polling
    ├── components/
    │   ├── common/
    │   │   ├── Navbar.jsx            # Top bar with branding, bell, and user pill
    │   │   ├── StatusBadge.jsx       # Status badges (TODO, IN_PROGRESS, BLOCKED, COMPLETED)
    │   │   ├── PriorityBadge.jsx     # Priority badges (LOW, MEDIUM, HIGH, URGENT)
    │   │   ├── RoleBadge.jsx         # RBAC role badges (ADMIN, CONTRIBUTOR, VIEWER)
    │   │   ├── Modal.jsx             # Accessible modal dialog
    │   │   ├── Toast.jsx             # Action feedback toast alerts
    │   │   ├── LoadingSpinner.jsx    # Clean loading rings
    │   │   └── EmptyState.jsx        # Contextual empty state illustrations
    │   ├── tasks/
    │   │   ├── TaskCard.jsx          # Kanban / grid task card with lifecycle dropdown
    │   │   ├── TaskTable.jsx         # Responsive task data table
    │   │   ├── TaskFilterBar.jsx     # Multi-select relational filters & text search
    │   │   ├── TaskFormModal.jsx     # Task create and edit modal with validation
    │   │   └── TaskAttachments.jsx   # Drag-and-drop 10MB file attachment zone
    │   ├── projects/
    │   │   ├── ProjectCard.jsx       # Workspace card with task counters
    │   │   ├── ProjectFormModal.jsx  # Project create/edit modal
    │   │   └── ProjectStatsCard.jsx  # SQL metrics and sprint progress bar
    │   └── notifications/
    │       └── NotificationDropdown.jsx # Navbar bell popover
    └── pages/
        ├── LoginPage.jsx             # Auth portal with 1-click demo accounts
        ├── DashboardPage.jsx         # Central command overview & high-level KPIs
        ├── TasksPage.jsx             # Comprehensive tasks directory (Table / Cards)
        ├── TaskDetailPage.jsx       # Full task view, lifecycle actions & attachments
        ├── KanbanPage.jsx            # Sprint Kanban board with 4 lifecycle columns
        ├── ProjectsPage.jsx          # Workspace directory
        ├── ProjectDetailPage.jsx     # Project workspace view with embedded Kanban
        ├── NotificationsPage.jsx     # Full notification center
        └── NotFoundPage.jsx          # 404 handler
```

---

## 3. Running the Application

### Development Server
```bash
cd frontend
npm install
npm run dev
```

Runs on: **`http://localhost:3000`**

### Production Build
```bash
cd frontend
npm run build
```

---

## 4. Test Accounts

Pre-seeded backend user accounts for quick testing:
- **Administrator**: `admin` / `admin123` (Full permissions)
- **Contributor**: `sarah.chen` / `user123` (Standard member)
- **Viewer**: `priya.qa` / `user123` (Read-only access)
