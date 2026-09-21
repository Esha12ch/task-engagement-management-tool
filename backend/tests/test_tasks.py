import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from datetime import date

import pytest # type: ignore
from fastapi.testclient import TestClient # type: ignore
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.pool import StaticPool # type: ignore

from app.database import Base, get_db
from app.main import app
from app.auth import hash_password
from app.models import (
    User,
    Client,
    ServiceType,
    TaskTemplate,
    Engagement,
    Task,
)


# ==========================================
# TEST DATABASE
# ==========================================

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# DATABASE OVERRIDE
# ==========================================

def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


# ==========================================
# FIXTURE
# ==========================================

@pytest.fixture(autouse=True)
def setup_database():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    # -----------------------------
    # Users
    # -----------------------------

    admin = User(
        name="Test Admin",
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        role="ADMIN",
        is_active=True
    )

    manager = User(
        name="Test Manager",
        email="manager@test.com",
        password_hash=hash_password("manager123"),
        role="MANAGER",
        is_active=True
    )

    member1 = User(
        name="Member One",
        email="member1@test.com",
        password_hash=hash_password("member123"),
        role="TEAM_MEMBER",
        is_active=True
    )

    member2 = User(
        name="Member Two",
        email="member2@test.com",
        password_hash=hash_password("member123"),
        role="TEAM_MEMBER",
        is_active=True
    )

    db.add_all([
        admin,
        manager,
        member1,
        member2
    ])

    db.commit()

    # -----------------------------
    # Client
    # -----------------------------

    test_client = Client(
        name="Test Client",
        email="client@test.com",
        phone="9999999999",
        is_active=True
    )

    db.add(test_client)
    db.commit()

    # -----------------------------
    # Service Type
    # -----------------------------

    service = ServiceType(
        name="Test Accounting",
        description="Test accounting service",
        engagement_type="RECURRING",
        is_active=True
    )

    db.add(service)
    db.commit()

    # -----------------------------
    # Task Template
    # -----------------------------

    template = TaskTemplate(
        service_type_id=service.id,
        name="Prepare Report",
        description="Prepare accounting report",
        default_days=2,
        sequence=1,
        is_active=True
    )

    db.add(template)
    db.commit()

    # -----------------------------
    # Engagement
    # -----------------------------

    engagement = Engagement(
        client_id=test_client.id,
        service_type_id=service.id,
        name="Test Engagement",
        period_start=date(2026, 9, 1),
        period_end=date(2026, 9, 30),
        due_date=date(2026, 9, 30),
        status="OPEN"
    )

    db.add(engagement)
    db.commit()

    # -----------------------------
    # Tasks
    # -----------------------------

    task1 = Task(
        engagement_id=engagement.id,
        assigned_to_id=member2.id,
        created_by_id=admin.id,
        title="Member Two Task",
        description="Task for member two",
        status="NOT_STARTED",
        due_date=date(2026, 9, 10)
    )

    task2 = Task(
        engagement_id=engagement.id,
        assigned_to_id=member1.id,
        created_by_id=admin.id,
        title="Member One Task",
        description="Task for member one",
        status="NOT_STARTED",
        due_date=date(2026, 9, 10)
    )

    db.add_all([
        task1,
        task2
    ])

    db.commit()
    db.close()


# ==========================================
# HELPER FUNCTION
# ==========================================

def login(email, password):

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


# ==========================================
# TEST 1
# TEAM MEMBER CANNOT UPDATE
# ANOTHER MEMBER'S TASK
# ==========================================

def test_member_cannot_update_another_members_task():

    headers = login(
        "member1@test.com",
        "member123"
    )

    response = client.put(
        "/tasks/1/status",
        json={
            "status": "IN_PROGRESS"
        },
        headers=headers
    )

    assert response.status_code == 403


# ==========================================
# TEST 2
# DUPLICATE ENGAGEMENT PREVENTION
# ==========================================

def test_duplicate_engagement_is_rejected():

    headers = login(
        "manager@test.com",
        "manager123"
    )

    response = client.post(
        "/engagements/",
        json={
            "client_id": 1,
            "service_type_id": 1,
            "name": "Duplicate Engagement",
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "due_date": "2026-09-30"
        },
        headers=headers
    )

    assert response.status_code == 409


# ==========================================
# TEST 3
# INVALID WORKFLOW TRANSITION
# ==========================================

def test_invalid_workflow_transition():

    headers = login(
        "member1@test.com",
        "member123"
    )

    response = client.put(
        "/tasks/2/status",
        json={
            "status": "COMPLETED"
        },
        headers=headers
    )

    assert response.status_code == 400


# ==========================================
# TEST 4
# MANAGER CAN APPROVE TASK
# ==========================================

def test_manager_can_approve_task():

    member_headers = login(
        "member1@test.com",
        "member123"
    )

    # NOT_STARTED -> IN_PROGRESS
    response = client.put(
        "/tasks/2/status",
        json={
            "status": "IN_PROGRESS"
        },
        headers=member_headers
    )

    assert response.status_code == 200

    # IN_PROGRESS -> READY_FOR_REVIEW
    response = client.put(
        "/tasks/2/status",
        json={
            "status": "READY_FOR_REVIEW"
        },
        headers=member_headers
    )

    assert response.status_code == 200

    # Login as Manager
    manager_headers = login(
        "manager@test.com",
        "manager123"
    )

    # READY_FOR_REVIEW -> COMPLETED
    response = client.put(
        "/tasks/2/status",
        json={
            "status": "COMPLETED"
        },
        headers=manager_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "COMPLETED"