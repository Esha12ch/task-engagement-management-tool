from datetime import date

from fastapi import APIRouter, Depends # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # type: ignore

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Task, User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# ==========================================
# DASHBOARD SUMMARY
# ==========================================

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    # --------------------------------------
    # Base query
    # --------------------------------------

    # Admin and Manager can see all tasks.
    # Team Member can see only assigned tasks.

    if current_user.role in ["ADMIN", "MANAGER"]:

        base_query = db.query(Task)

    else:

        base_query = (
            db.query(Task)
            .filter(
                Task.assigned_to_id == current_user.id
            )
        )

    # --------------------------------------
    # Open tasks
    # --------------------------------------

    open_tasks = (
        base_query
        .filter(Task.status != "COMPLETED")
        .count()
    )

    # --------------------------------------
    # Overdue tasks
    # --------------------------------------

    overdue_tasks = (
        base_query
        .filter(
            Task.due_date < today,
            Task.status != "COMPLETED"
        )
        .count()
    )

    # --------------------------------------
    # Due today
    # --------------------------------------

    due_today = (
        base_query
        .filter(
            Task.due_date == today,
            Task.status != "COMPLETED"
        )
        .count()
    )

    # --------------------------------------
    # Waiting for client
    # --------------------------------------

    waiting_for_client = (
        base_query
        .filter(
            Task.status == "WAITING_FOR_CLIENT"
        )
        .count()
    )

    # --------------------------------------
    # Waiting for review
    # --------------------------------------

    waiting_for_review = (
        base_query
        .filter(
            Task.status == "READY_FOR_REVIEW"
        )
        .count()
    )

    # --------------------------------------
    # Completed
    # --------------------------------------

    completed_tasks = (
        base_query
        .filter(
            Task.status == "COMPLETED"
        )
        .count()
    )

    # --------------------------------------
    # Total
    # --------------------------------------

    total_tasks = base_query.count()

    return {
        "total_tasks": total_tasks,
        "open_tasks": open_tasks,
        "overdue_tasks": overdue_tasks,
        "due_today": due_today,
        "waiting_for_client": waiting_for_client,
        "waiting_for_review": waiting_for_review,
        "completed_tasks": completed_tasks
    }