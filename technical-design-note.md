# Technical Design Note

## Task & Engagement Management Tool

### 1. Overview

The Task & Engagement Management Tool is a full-stack application designed to manage professional services work across clients, engagements, tasks, users, and service types.

The system supports role-based access for Admins, Managers, and Team Members. It provides task assignment, workflow management, automatic task generation from service templates, recurring engagements, dashboard reporting, and audit history.

The backend is responsible for authentication, authorization, validation, workflow enforcement, business logic, and database operations.

The frontend provides the user interface for interacting with the system.

---

## 2. Architecture

The application follows a simple layered architecture.

```text
                    React Frontend
                         |
                         | HTTP / REST API
                         v
                  FastAPI Backend
                         |
             +-----------+-----------+
             |                       |
             v                       v
       API Routers              Service Layer
             |                       |
             +-----------+-----------+
                         |
                         v
                    SQLAlchemy
                         |
                         v
                     SQLite

Frontend

The frontend is built using React with Vite.

It is responsible for:

User interface
Navigation
Forms
Dashboard display
Task and engagement management
Sending authenticated API requests

Axios is used for communication with the FastAPI backend.

Backend

The backend is built using FastAPI.

It is responsible for:

REST API endpoints
Authentication
Authorization
Request validation
Business rules
Task workflow validation
Engagement and task generation
Audit logging
Database operations
Database

SQLite is used as the database for the assignment.

SQLAlchemy is used as the ORM to define models, relationships, constraints, and database operations.

Authentication

JWT tokens are used for authentication.

After successful login, the backend generates an access token. The frontend sends the token with protected API requests using the Authorization: Bearer <token> header.

Deployment

The current implementation is configured for local development.

For production deployment, the React frontend can be deployed separately from the FastAPI backend, with a production database such as PostgreSQL replacing SQLite for higher scale and concurrency.

## 3. Database Schema

The application uses SQLAlchemy ORM with SQLite.

### Main Entities

#### User

Stores application users and their roles.

- Primary Key: `id`
- Unique field: `email`
- Role: `ADMIN`, `MANAGER`, or `TEAM_MEMBER`
- Stores a hashed password
- `is_active` controls whether the user can access protected resources

#### Client

Stores client information.

- Primary Key: `id`
- Client name
- Email
- Phone
- Active/inactive status

A client can have multiple engagements.

#### ServiceType

Defines the type of professional service.

- Primary Key: `id`
- Service name
- Description
- Engagement type
- Active/inactive status

A service type can have multiple task templates and engagements.

#### TaskTemplate

Defines the tasks that should be generated for a service.

- Primary Key: `id`
- Foreign Key: `service_type_id`
- Task name
- Description
- Default number of days
- Sequence/order
- Active/inactive status

#### Engagement

Represents a service engagement for a client and period.

- Primary Key: `id`
- Foreign Key: `client_id`
- Foreign Key: `service_type_id`
- Engagement name
- Period start
- Period end
- Due date
- Status

A database constraint prevents duplicate engagements for the same client, service type, and period.

#### Task

Represents an individual piece of work.

- Primary Key: `id`
- Foreign Key: `engagement_id`
- Foreign Key: `assigned_to_id`
- Foreign Key: `created_by_id`
- Title
- Description
- Status
- Due date
- Submitted timestamp
- Completed timestamp
- Created and updated timestamps

Indexes are maintained on frequently queried fields such as:

- `assigned_to_id`
- `status`
- `due_date`
- `engagement_id`

#### AuditLog

Stores important task activity.

- Primary Key: `id`
- Foreign Key: `user_id`
- Foreign Key: `task_id`
- Action
- Previous value
- New value
- Timestamp

### Entity Relationships

```text
User
 |
 +--------------------+
 |                    |
 v                    v
Task              AuditLog
 |
 |
 v
Engagement
 |
 +-------------------+
 |                   |
 v                   v
Client          ServiceType
                    |
                    v
              TaskTemplate

## 4. Backend Design

The backend follows a router, service, and database model structure.

### API Routers

FastAPI routers separate the application functionality into different modules:

- `auth.py` — authentication and current-user endpoints
- `users.py` — user management
- `clients.py` — client management
- `services.py` — service type management
- `templates.py` — task template management
- `engagements.py` — engagement creation and management
- `tasks.py` — task access, assignment, and status updates
- `audit.py` — audit history
- `dashboard.py` — dashboard summaries

### Service Layer

Business logic that is more complex than simple CRUD operations is kept in service modules.

#### Engagement Service

`engagement_service.py` handles:

- Client and service validation
- Engagement validation
- Duplicate engagement prevention
- Task generation from templates
- Task due-date calculation
- Recurring engagement generation
- Database transactions

#### Task Service

`task_service.py` handles:

- Task access validation
- Task ownership validation
- Task assignment
- Task status transitions
- Manager review rules
- Audit logging

### Validation

Validation is performed at multiple levels.

#### API Validation

Pydantic schemas validate incoming request data and response structures.

#### Business Validation

The service layer validates business rules such as:

- Valid engagement dates
- Active clients and services
- Duplicate engagements
- Valid task status transitions
- Task ownership
- Valid task assignments

#### Database Validation

Database constraints are used for data integrity, including:

- Unique email addresses
- Unique service names
- Foreign key relationships
- Unique engagement period combinations

### Error Handling

The backend uses FastAPI `HTTPException` responses for invalid operations.

Examples include:

- `400 Bad Request` for invalid business operations
- `401 Unauthorized` for invalid authentication
- `403 Forbidden` for authorization failures
- `404 Not Found` when a requested resource does not exist
- `409 Conflict` for duplicate resources

This keeps API responses predictable and allows the frontend to display appropriate error messages.

### Transactions

Engagement creation and automatic task generation are handled within a database transaction.

If task generation fails, the transaction can be rolled back so that the system does not leave a partially created engagement.

---
Step 4 — Authentication & Authorization

Add this below Backend Design:

## 5. Authentication & Authorization

The application uses JWT-based authentication and role-based authorization.

### Authentication Flow

```text
User
 |
 v
Login
 |
 v
POST /auth/login
 |
 v
Validate Email + Password
 |
 v
Generate JWT Access Token
 |
 v
Frontend Stores Token
 |
 v
Protected API Request
 |
 v
Backend Validates JWT
 |
 v
Identify Current User

Passwords are stored as hashed values using Passlib with bcrypt.

The JWT contains the authenticated user's identifier and is validated by the backend before accessing protected endpoints.

Role-Based Authorization

The system supports three roles:

ADMIN
MANAGER
TEAM_MEMBER

Backend dependencies are used to restrict endpoints based on user roles.

Authorization Rules
Action	Admin	Manager	Team Member
Manage Users	Yes	No	No
Manage Clients	Yes	No	No
Manage Service Types	Yes	No	No
Manage Task Templates	Yes	No	No
Create Engagements	Yes	Yes	No
Assign Tasks	Yes	Yes	No
View Team Tasks	Yes	Yes	No
Update Own Tasks	Yes	Yes	Yes
Approve Tasks	Yes	Yes	No
Request Changes	Yes	Yes	No
View Audit History	Yes	Yes	No
Task Ownership

Team Members are only allowed to access and update tasks assigned to themselves.

For example, if Team Member A attempts to update a task assigned to Team Member B, the backend rejects the request with a 403 Forbidden response.

Server-Side Enforcement

Authorization is enforced by the backend rather than relying only on frontend controls.

This prevents users from bypassing permissions by directly calling the API.

## 6. Recurring Task Generation

Recurring services can generate tasks for the next service period.

### Generation Process

When a recurring engagement requests the next period:

1. The existing engagement is identified.
2. The system checks that the service is configured as recurring.
3. The next period is calculated based on the existing engagement period.
4. The system checks whether an engagement already exists for the same client, service type, and period.
5. Active task templates for the service are loaded.
6. A new engagement is created.
7. Tasks are generated from the active templates.
8. Task due dates are calculated from the template configuration.
9. The new engagement and tasks are committed to the database.

### Duplicate Prevention

A database constraint is used to prevent duplicate engagements for the same:

- Client
- Service Type
- Period Start
- Period End

If the next period already exists, the generation request is rejected instead of creating duplicate data.

### Failure Handling

Engagement creation and task generation are performed within a database transaction.

If an error occurs during the operation, the transaction can be rolled back so that the system does not leave a partially generated engagement with incomplete tasks.

This provides safer repeated execution and maintains data consistency.

---
## 7. Workflow Rules

The backend enforces the allowed task status transitions.

### Allowed Transitions

| Current Status | Allowed Next Status |
|---|---|
| `NOT_STARTED` | `IN_PROGRESS` |
| `IN_PROGRESS` | `WAITING_FOR_CLIENT`, `READY_FOR_REVIEW` |
| `WAITING_FOR_CLIENT` | `IN_PROGRESS` |
| `READY_FOR_REVIEW` | `COMPLETED`, `CHANGES_REQUESTED` |
| `CHANGES_REQUESTED` | `IN_PROGRESS` |
| `COMPLETED` | No further transition |

### Team Member Workflow

A Team Member can:

- Move `NOT_STARTED` → `IN_PROGRESS`
- Move `IN_PROGRESS` → `WAITING_FOR_CLIENT`
- Move `IN_PROGRESS` → `READY_FOR_REVIEW`
- Move `WAITING_FOR_CLIENT` → `IN_PROGRESS`
- Move `CHANGES_REQUESTED` → `IN_PROGRESS`

A Team Member cannot directly mark a task as `COMPLETED`.

### Manager Review

When a task reaches `READY_FOR_REVIEW`, an authorized Manager can:

- Approve the task: `READY_FOR_REVIEW` → `COMPLETED`
- Request changes: `READY_FOR_REVIEW` → `CHANGES_REQUESTED`

When changes are requested, the Team Member can move the task back to `IN_PROGRESS`.

### Invalid Transitions

Any transition that is not defined in the workflow is rejected by the backend.

This prevents users from bypassing the intended task lifecycle through direct API requests.

---

## 8. Testing

The backend is tested using Pytest and HTTPX.

The tests focus on important business and authorization rules rather than only testing simple API responses.

### Current Backend Tests

The test suite covers:

1. A Team Member cannot update another Team Member's task.
2. Duplicate engagement creation is rejected.
3. Invalid task workflow transitions are rejected.
4. A Manager can approve and complete a task.

### Test Result

The current local test suite passes successfully:

```text
4 passed

Production Considerations

Add this below Testing:

## 9. Production Considerations

The current application uses SQLite because it is lightweight and suitable for the assignment and local development.

For a production environment with millions of tasks, the following improvements would be considered.

### Database Indexing

Indexes should be maintained on frequently queried fields such as:

- `assigned_to_id`
- `status`
- `due_date`
- `engagement_id`

These indexes improve task filtering, assignment queries, and dashboard queries.

### Pagination

Task APIs should use pagination instead of returning large numbers of records in a single request.

Example:

```text
GET /tasks/?skip=0&limit=20

This reduces response size and improves frontend performance.

Background Jobs

Scheduled and heavy operations can be moved to background workers.

Examples:

Recurring task generation
Notifications
Scheduled processing
Large data operations
Dashboard Optimization

Dashboard statistics should use database aggregation queries rather than loading all tasks into application memory.

Examples include:

Total task count
Open task count
Overdue task count
Waiting-for-client count
Waiting-for-review count
Database Scaling

For a large production workload, SQLite can be replaced with PostgreSQL.

Additional scaling options include:

Connection pooling
Query optimization
Caching
Read replicas
Partitioning where appropriate
Logging and Monitoring

A production deployment should include:

Structured application logs
Error monitoring
API monitoring
Database monitoring
Request tracing where required


Technical Decisions & Trade-offs

## 10. Technical Decisions and Trade-offs

### FastAPI

FastAPI was selected for the backend because it provides:

- Automatic API documentation
- Request validation
- Dependency injection
- Clear API organization
- Good performance

### SQLAlchemy

SQLAlchemy was selected to provide:

- ORM-based database access
- Entity relationships
- Database constraints
- Transaction management
- Maintainable database code

### SQLite

SQLite was selected because the assignment is a small, self-contained application and SQLite requires minimal configuration.

For a production environment with millions of tasks and concurrent users, PostgreSQL would be more appropriate.

### Server-Side Authorization

Authorization is implemented on the backend instead of relying only on frontend controls.

This ensures that users cannot bypass permissions by directly calling the API.

For example, a Team Member attempting to update another user's task is rejected by the backend even if the request is sent directly to the API.

---

Security Considerations
## 11. Security Considerations

The application includes several backend security controls.

### Password Security

User passwords are stored as hashed passwords using bcrypt rather than storing plain-text passwords.

### JWT Authentication

Protected API endpoints require a valid JWT access token.

### Role-Based Authorization

Backend endpoints verify the user's role before allowing restricted operations.

### Task Ownership

Team Members can only access and update tasks assigned to themselves.

### Server-Side Validation

Important business rules are validated on the backend so they cannot be bypassed by modifying frontend requests.

### Workflow Validation

Task status transitions are validated by backend business logic to prevent invalid workflow changes.

### Active User Validation

Inactive users are prevented from accessing protected resources.

Frontend controls are treated as user-interface restrictions only. Security decisions are enforced by the backend.

## 12. Conclusion

The application provides a complete task and engagement management workflow for a professional services team.

The design focuses on:

- Clear separation between frontend and backend responsibilities
- Server-side authentication and authorization
- Strong business-rule validation
- Controlled task workflows
- Automatic task generation
- Duplicate prevention
- Audit history
- Automated backend testing
- Scalability considerations for future growth

The current implementation is designed as a small, maintainable assignment solution while documenting the changes required for a larger production environment.
