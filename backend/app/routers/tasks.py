from fastapi import APIRouter, Depends, HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Task, User
from ..schemas import (
    TaskAssignRequest,
    TaskResponse,
    TaskStatusUpdate
)
from ..services.task_service import (
    assign_task,
    get_task_by_id,
    update_task_status,
    update_task_deadline
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# ==========================================
# GET ALL TASKS
# ==========================================

@router.get(
    "/",
    response_model=list[TaskResponse]
)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Admin and Manager can see all tasks
    if current_user.role in ["ADMIN", "MANAGER"]:

        tasks = (
            db.query(Task)
            .order_by(Task.id.desc())
            .all()
        )

        return tasks

    # Team Member can see only own tasks
    tasks = (
        db.query(Task)
        .filter(
            Task.assigned_to_id == current_user.id
        )
        .order_by(Task.id.desc())
        .all()
    )

    return tasks


# ==========================================
# GET SINGLE TASK
# ==========================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = get_task_by_id(
        db,
        task_id
    )

    # Team Member can only see own task
    if current_user.role == "TEAM_MEMBER":

        if task.assigned_to_id != current_user.id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access tasks assigned to you"
            )

    return task


# ==========================================
# ASSIGN / REASSIGN TASK
# ==========================================

@router.put(
    "/{task_id}/assign",
    response_model=TaskResponse
)
def assign_task_to_member(
    task_id: int,
    assignment_data: TaskAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = assign_task(
        db=db,
        task_id=task_id,
        assigned_to_id=assignment_data.assigned_to_id,
        current_user=current_user
    )

    return task
# ==========================================
# UPDATE TASK DEADLINE
# ==========================================

@router.put(
    "/{task_id}/deadline",
    response_model=TaskResponse
)
def change_task_deadline(
    task_id: int,
    deadline_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    due_date = deadline_data.get("due_date")

    if not due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date is required"
        )

    try:
        from datetime import date

        due_date = date.fromisoformat(
            due_date
        )

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    task = update_task_deadline(
        db=db,
        task_id=task_id,
        due_date=due_date,
        current_user=current_user
    )

    return task

# ==========================================
# UPDATE TASK STATUS
# ==========================================

@router.put(
    "/{task_id}/status",
    response_model=TaskResponse
)
def change_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    task = update_task_status(
        db=db,
        task_id=task_id,
        new_status=status_data.status,
        current_user=current_user
    )

    return task