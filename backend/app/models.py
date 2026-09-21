from datetime import datetime, date
from enum import Enum

from sqlalchemy import (  # type: ignore[reportMissingImports]
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    UniqueConstraint,
    Index
)

from sqlalchemy.orm import relationship  # type: ignore[reportMissingImports]

from .database import Base


# =========================
# ENUMS
# =========================

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    TEAM_MEMBER = "TEAM_MEMBER"


class EngagementType(str, Enum):
    ONE_TIME = "ONE_TIME"
    RECURRING = "RECURRING"


class TaskStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_FOR_CLIENT = "WAITING_FOR_CLIENT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"
    COMPLETED = "COMPLETED"


# =========================
# USER
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(30),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships

    assigned_tasks = relationship(
        "Task",
        foreign_keys="Task.assigned_to_id",
        back_populates="assignee"
    )

    created_tasks = relationship(
        "Task",
        foreign_keys="Task.created_by_id",
        back_populates="creator"
    )


# =========================
# CLIENT
# =========================

class Client(Base):
    __tablename__ = "clients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(150),
        nullable=True
    )

    phone = Column(
        String(30),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    engagements = relationship(
        "Engagement",
        back_populates="client"
    )


# =========================
# SERVICE TYPE
# =========================

class ServiceType(Base):
    __tablename__ = "service_types"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )

    engagement_type = Column(
        String(30),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    task_templates = relationship(
        "TaskTemplate",
        back_populates="service_type",
        cascade="all, delete-orphan"
    )

    engagements = relationship(
        "Engagement",
        back_populates="service_type"
    )


# =========================
# TASK TEMPLATE
# =========================

class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service_type_id = Column(
        Integer,
        ForeignKey("service_types.id"),
        nullable=False
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    default_days = Column(
        Integer,
        nullable=False,
        default=0
    )

    sequence = Column(
        Integer,
        nullable=False,
        default=1
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    service_type = relationship(
        "ServiceType",
        back_populates="task_templates"
    )


# =========================
# ENGAGEMENT
# =========================

class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    client_id = Column(
        Integer,
        ForeignKey("clients.id"),
        nullable=False
    )

    service_type_id = Column(
        Integer,
        ForeignKey("service_types.id"),
        nullable=False
    )

    name = Column(
        String(200),
        nullable=False
    )

    period_start = Column(
        Date,
        nullable=False
    )

    period_end = Column(
        Date,
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    client = relationship(
        "Client",
        back_populates="engagements"
    )

    service_type = relationship(
        "ServiceType",
        back_populates="engagements"
    )

    tasks = relationship(
        "Task",
        back_populates="engagement",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "service_type_id",
            "period_start",
            "period_end",
            name="uq_client_service_period"
        ),
    )


# =========================
# TASK
# =========================

class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    engagement_id = Column(
        Integer,
        ForeignKey("engagements.id"),
        nullable=False
    )

    assigned_to_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(200),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(40),
        nullable=False,
        default=TaskStatus.NOT_STARTED.value
    )

    due_date = Column(
        Date,
        nullable=False
    )

    submitted_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    engagement = relationship(
        "Engagement",
        back_populates="tasks"
    )

    assignee = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        back_populates="assigned_tasks"
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_tasks"
    )

    __table_args__ = (
        Index(
            "idx_task_assigned_status",
            "assigned_to_id",
            "status"
        ),
        Index(
            "idx_task_due_date",
            "due_date"
        ),
        Index(
            "idx_task_engagement",
            "engagement_id"
        ),
    )


# =========================
# AUDIT LOG
# =========================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=True
    )

    action = Column(
        String(100),
        nullable=False
    )

    old_value = Column(
        String(100),
        nullable=True
    )

    new_value = Column(
        String(100),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )