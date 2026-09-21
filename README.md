# Task & Engagement Management Tool

A full-stack Task & Engagement Management Tool built for a professional services team.

The application manages users, clients, service types, task templates, engagements, tasks, task assignments, task workflows, dashboards, and audit history with authentication and role-based authorization.

---

## Features

- JWT-based authentication
- Role-based authorization
- Admin, Manager, and Team Member roles
- User management
- Client management
- Service Type management
- Task Template management
- Engagement management
- Automatic task generation from service templates
- Recurring engagement support
- Task assignment and reassignment
- Task workflow validation
- Waiting for Client workflow
- Changes Requested workflow
- Manager task review and approval
- Dashboard task summaries
- Audit history
- Duplicate engagement prevention
- Server-side validation
- SQLite database with SQLAlchemy
- Backend automated tests
- React frontend

---

# Tech Stack

## Frontend

- React
- Vite
- Axios
- React Router

## Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication
- Passlib
- bcrypt

## Database

- SQLite

## Testing

- Pytest
- HTTPX

---

# User Roles

## Admin

Admin users can:

- Manage users
- Create and manage clients
- Create and manage service types
- Create and manage task templates
- View engagements
- View tasks
- Assign tasks

## Manager

Managers can:

- Create engagements
- Manage engagements
- Assign and reassign tasks
- View team tasks
- Review submitted tasks
- Approve tasks
- Request changes
- View audit history
- View dashboard information

## Team Member

Team members can:

- View their assigned tasks
- Update their own task status
- Move tasks to Waiting for Client
- Submit tasks for review
- Move Changes Requested tasks back to In Progress

Team members cannot:

- Update another user's task
- Assign or reassign tasks
- Approve tasks
- Access manager/admin-only functionality

All important authorization rules are enforced on the backend.

---

# Task Workflow

The backend validates task status transitions.

The supported workflow is:

```text
NOT_STARTED
      |
      v
IN_PROGRESS
      |
      +-------------------------+
      |                         |
      v                         v
WAITING_FOR_CLIENT       READY_FOR_REVIEW
      |                         |
      |                         +----------------+
      |                         |                |
      v                         v                v
IN_PROGRESS             CHANGES_REQUESTED   COMPLETED
                              |
                              v
                         IN_PROGRESS

```

---

# Project Structure

```text
Task Management Assignment/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── dependencies.py
│   │
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── clients.py
│   │   │   ├── services.py
│   │   │   ├── templates.py
│   │   │   ├── engagements.py
│   │   │   ├── tasks.py
│   │   │   ├── audit.py
│   │   │   └── dashboard.py
│   │
│   │   └── services/
│   │       ├── engagement_service.py
│   │       └── task_service.py
│   │
│   ├── tests/
│   │   └── test_tasks.py
│   │
│   ├── seed.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── README.md
├── technical-design-note.md
└── ERD.png
```

# Backend Setup

## 1. Open the backend directory

```powershell
cd "C:\Users\Esha Chauhan\Downloads\Task Management Assignment\backend"
2. Activate the virtual environment
.\venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Start the backend
uvicorn app.main:app --reload --port 8001

The backend will run at:

http://127.0.0.1:8001

# Frontend Setup

Open a second terminal.

## 1. Open the frontend directory

```powershell
cd "C:\Users\Esha Chauhan\Downloads\Task Management Assignment\frontend"
2. Install dependencies
npm install
3. Start the frontend
npm run dev

The frontend will run at:

http://localhost:5173

# API Documentation

FastAPI automatically provides Swagger API documentation.

## Swagger UI

`http://127.0.0.1:8001/docs`

## OpenAPI Specification

`http://127.0.0.1:8001/openapi.json`

# Demo Credentials

## Admin

- Email: `admin@example.com`
- Password: `admin123`

## Manager

- Email: `manager1@example.com`
- Password: `manager123`

## Team Member

- Email: `member1@example.com`
- Password: `member123`

> These credentials are intended for the local/demo environment.

---

# Authorization

Authorization is enforced on the backend rather than relying only on frontend controls.

Examples:

- Admin-only operations require the Admin role.
- Managers can assign and reassign tasks.
- Team Members can only update tasks assigned to themselves.
- Team Members cannot update another Team Member's task.
- Team Members cannot assign tasks.
- Team Members cannot approve tasks.
- Team Members cannot access audit history.
- Inactive users cannot access protected resources.
- Invalid task status transitions are rejected by the backend.

All important authorization rules are enforced server-side.

---

# Database Design

The main entities in the application are:

- `User`
- `Client`
- `ServiceType`
- `TaskTemplate`
- `Engagement`
- `Task`
- `AuditLog`

## Main Relationships

```text
Client
   |
   └── Engagement
          |
          └── Task

ServiceType
   |
   ├── TaskTemplate
   |
   └── Engagement

User
   |
   ├── Task
   |
   └── AuditLog

# Engagement and Task Generation

When an engagement is created:

1. The client is validated.
2. The selected service type is validated.
3. Active task templates for the selected service are loaded.
4. The engagement is created.
5. Tasks are automatically generated from the selected templates.
6. Task due dates are calculated using the template configuration.
7. The operation is handled within a database transaction.
8. Duplicate engagements for the same client, service, and period are prevented.

---
Recurring Engagements

Recurring services can generate the next period automatically.

Before creating the next period, the backend checks whether an engagement already exists for the same:

Client
Service Type
Period

If the next-period engagement already exists, the backend rejects the request and prevents duplicate engagement and task creation.

This duplicate check prevents duplicate recurring engagements and duplicate generated tasks.

Task Assignment

Admin and Manager users can assign and reassign tasks to active Team Members.

Team Members cannot assign or reassign tasks.

Task assignment changes are recorded in the audit history.

Task Review

When a Team Member completes their work, they can submit the task for review:

READY_FOR_REVIEW

A Manager can then:

READY_FOR_REVIEW → COMPLETED

or:

READY_FOR_REVIEW → CHANGES_REQUESTED

If changes are requested:

CHANGES_REQUESTED → IN_PROGRESS

The workflow is enforced by backend business logic.

Audit History

Important task actions are recorded in the audit log.

The audit log records:

User
Task
Action
Previous value
New value
Timestamp

Examples include:

Task assignment
Status change

Audit history is restricted to authorized roles.

Dashboard

The dashboard provides task-level summaries including:

Total Tasks
Open Tasks
Overdue Tasks
Due Today
Waiting for Client
Waiting for Review
Completed Tasks

The dashboard is role-aware and uses the authenticated user's permissions.

Sample Data

The seed script creates demonstration data including:

1 Admin
2 Managers
4 Team Members
5 Clients
3 Service Types
Task Templates
Recurring Engagements
20+ Tasks

To seed the database:

cd "C:\Users\Esha Chauhan\Downloads\Task Management Assignment\backend"
.\venv\Scripts\Activate.ps1
python seed.py
Testing

Backend tests are implemented using Pytest.

Run the tests with:

cd "C:\Users\Esha Chauhan\Downloads\Task Management Assignment\backend"
.\venv\Scripts\Activate.ps1
pytest -v

The implemented tests cover important backend scenarios including:

Team Member cannot update another Team Member's task.
Duplicate engagement creation is rejected.
Invalid task workflow transitions are rejected.
Manager can approve/complete a task.

Expected local test result:

4 passed
Production Considerations

The current application uses SQLite because it is lightweight and suitable for the assignment and local development.

If the system grows to approximately 5 million tasks, several areas would need to be reconsidered.

Database Indexes

Indexes should be maintained on frequently queried columns such as:

assigned_to_id
status
due_date
engagement_id

These indexes help improve task filtering, assignment queries, and dashboard queries.

Pagination

The task API should not return millions of records in a single request.

A paginated API can be used:

GET /tasks/?skip=0&limit=20

This reduces response size and improves frontend performance.

Background Jobs

Recurring engagement generation and other scheduled operations can be moved to background workers.

Examples include:

Recurring task generation
Notifications
Scheduled processing
Large data operations
Dashboard Queries

Dashboard statistics should be calculated using efficient database aggregation queries instead of loading all tasks into application memory.

Examples include:

COUNT total tasks
COUNT open tasks
COUNT overdue tasks
COUNT waiting-for-client tasks
COUNT waiting-for-review tasks
Logging and Monitoring

A production deployment should include:

Structured application logs
Error monitoring
API monitoring
Database monitoring
Request tracing where required
Database Scaling

For a large production workload, SQLite could be replaced with PostgreSQL.

Additional improvements could include:

Database connection pooling
Read replicas
Query optimization
Caching
Partitioning where appropriate
Technical Decisions and Trade-offs
FastAPI

FastAPI was selected because it provides:

Automatic API documentation
Request validation
Dependency injection
Clear API organization
Good performance
SQLAlchemy

SQLAlchemy was selected to provide:

ORM-based database access
Relationships between entities
Database constraints
Transaction management
Maintainable database code
SQLite

SQLite was selected because the assignment is a small self-contained application and SQLite requires minimal configuration.

For a production environment with millions of tasks and concurrent users, PostgreSQL would be more appropriate.

Server-Side Authorization

Authorization is implemented on the backend so that users cannot bypass permissions by modifying frontend requests.

For example, a Team Member attempting to update another user's task is rejected by the backend even if they manually call the API.

Security Considerations

The application includes several backend security controls:

Password hashing
JWT authentication
Protected API endpoints
Role-based authorization
Task ownership validation
Server-side workflow validation
Active-user validation

Frontend controls are treated as a user-interface convenience; security decisions are enforced by the backend.

Running the Complete Application
Terminal 1 — Backend
cd "C:\Users\Esha Chauhan\Downloads\Task Management Assignment\backend"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
Terminal 2 — Frontend
cd "C:\Users\Esha Chauhan\Downloads\Task Management Assignment\frontend"
npm run dev

Then open:

http://localhost:5173

Application Status

The application implements the core Task & Engagement Management workflow, including:

Authentication
Role-based authorization
User management
Client management
Service Type management
Task Template management
Engagement management
Automatic task generation
Recurring engagement support
Task assignment and reassignment
Task workflow validation
Manager review
Dashboard reporting
Audit history
Sample data
Backend automated tests
React frontend

