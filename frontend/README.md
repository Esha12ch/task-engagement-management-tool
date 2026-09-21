# Task & Engagement Management Tool

A full-stack Task & Engagement Management Tool built for a professional services team.

The application allows teams to manage clients, service types, engagements, task templates, tasks, assignments, approvals, workflows, dashboards, and audit history with role-based access control.

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
- Automatic task generation from templates
- Recurring engagement support
- Task assignment and reassignment
- Task status workflow validation
- Waiting for Client workflow
- Changes Requested workflow
- Dashboard task summaries
- Audit history
- Duplicate engagement prevention
- Server-side validation
- SQLite database with SQLAlchemy
- Backend automated tests
- React frontend

---

## Tech Stack

### Frontend

- React
- Vite
- Axios
- React Router

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT
- Passlib
- bcrypt
- Pytest

### Database

- SQLite

---

## User Roles

### Admin

Admin can:

- Manage users
- Create and manage clients
- Create and manage service types
- Create and manage task templates
- View engagements and tasks
- Assign tasks

### Manager

Manager can:

- Create and manage engagements
- Assign and reassign tasks
- View team tasks
- Review submitted tasks
- Approve tasks
- Request changes
- View audit history
- View dashboard information

### Team Member

Team members can:

- View their assigned tasks
- Update their own task status
- Mark tasks as Waiting for Client
- Submit tasks for review
- Move Changes Requested tasks back to In Progress

Team members cannot:

- Update another user's task
- Assign tasks
- Approve tasks
- Access manager/admin-only functionality

---

## Task Workflow

The backend enforces the following workflow:

```text
NOT_STARTED
     |
     v
IN_PROGRESS
     |
     +----------------------+
     |                      |
     v                      v
WAITING_FOR_CLIENT    READY_FOR_REVIEW
     |                      |
     v                      +-------------+
IN_PROGRESS                 |             |
                            v             v
                    CHANGES_REQUESTED  COMPLETED
                            |
                            v
                       IN_PROGRESS

                       