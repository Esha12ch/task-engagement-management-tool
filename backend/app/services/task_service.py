from datetime import datetime

from fastapi import HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..models import AuditLog, Task, User


# ==========================================
# GET TASK
# ==========================================

def get_task_by_id(
    db: Session,
    task_id: int
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


# ==========================================
# CHECK TASK ACCESS
# ==========================================

def check_task_access(
    task: Task,
    current_user: User
):
    """
    Admin and Manager can access all tasks.

    Team Member can access only tasks
    assigned to themselves.
    """

    if current_user.role in ["ADMIN", "MANAGER"]:
        return

    if current_user.role == "TEAM_MEMBER":

        if task.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access tasks assigned to you"
            )

        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this task"
    )


# ==========================================
# ASSIGN / REASSIGN TASK
# ==========================================

def assign_task(
    db: Session,
    task_id: int,
    assigned_to_id: int,
    current_user: User
):
    """
    Only Admin or Manager can assign/reassign tasks.
    """

    # Get task
    task = get_task_by_id(
        db,
        task_id
    )

    # Check assigning user role
    if current_user.role not in ["ADMIN", "MANAGER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin or Manager can assign tasks"
        )

    # Find team member
    team_member = (
        db.query(User)
        .filter(
            User.id == assigned_to_id,
            User.is_active == True
        )
        .first()
    )

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    # Only Team Members can receive tasks
    if team_member.role != "TEAM_MEMBER":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tasks can only be assigned to Team Members"
        )

    # Store old assignment
    old_assigned_to = task.assigned_to_id

    # Assign task
    task.assigned_to_id = assigned_to_id
    task.updated_at = datetime.utcnow()

    # Create audit log
    audit = AuditLog(
        user_id=current_user.id,
        task_id=task.id,
        action="TASK_ASSIGNED",
        old_value=(
            str(old_assigned_to)
            if old_assigned_to is not None
            else None
        ),
        new_value=str(assigned_to_id)
    )

    db.add(audit)

    db.commit()
    db.refresh(task)

    return task
# ==========================================
# UPDATE TASK DEADLINE
# ==========================================

def update_task_deadline(
    db: Session,
    task_id: int,
    due_date,
    current_user: User
):
    """
    Only Admin or Manager can set/change
    a task deadline.
    """

    # Get task
    task = get_task_by_id(
        db,
        task_id
    )

    # Only Admin or Manager
    if current_user.role not in [
        "ADMIN",
        "MANAGER"
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin or Manager can set task deadlines"
        )

    # Store old deadline
    old_due_date = task.due_date

    # Update deadline
    task.due_date = due_date
    task.updated_at = datetime.utcnow()

    # Create audit log
    audit = AuditLog(
        user_id=current_user.id,
        task_id=task.id,
        action="DEADLINE_UPDATED",
        old_value=(
            str(old_due_date)
            if old_due_date is not None
            else None
        ),
        new_value=(
            str(due_date)
            if due_date is not None
            else None
        )
    )

    db.add(audit)

    db.commit()
    db.refresh(task)

    return task

# ==========================================
# VALID WORKFLOW TRANSITIONS
# ==========================================

ALLOWED_TRANSITIONS = {

    "NOT_STARTED": [
        "IN_PROGRESS"
    ],

    "IN_PROGRESS": [
        "WAITING_FOR_CLIENT",
        "READY_FOR_REVIEW"
    ],

    "WAITING_FOR_CLIENT": [
        "IN_PROGRESS"
    ],

    "READY_FOR_REVIEW": [
        "COMPLETED",
        "CHANGES_REQUESTED"
    ],

    "CHANGES_REQUESTED": [
        "IN_PROGRESS"
    ],

    "COMPLETED": []
}


# ==========================================
# UPDATE TASK STATUS
# ==========================================

def update_task_status(
    db: Session,
    task_id: int,
    new_status: str,
    current_user: User
):
    """
    Update task status while enforcing
    workflow and authorization rules.
    """

    # Get task
    task = get_task_by_id(
        db,
        task_id
    )

    old_status = task.status

    # --------------------------------------
    # Check whether transition is valid
    # --------------------------------------

    allowed_statuses = ALLOWED_TRANSITIONS.get(
        old_status,
        []
    )

    if new_status not in allowed_statuses:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid workflow transition: "
                f"{old_status} -> {new_status}"
            )
        )

    # --------------------------------------
    # TEAM MEMBER RULES
    # --------------------------------------

    if current_user.role == "TEAM_MEMBER":

        # Team member can only modify own task
        if task.assigned_to_id != current_user.id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update tasks assigned to you"
            )

        # Team member cannot approve work
        if new_status == "COMPLETED":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team Members cannot approve tasks"
            )

    # --------------------------------------
    # MANAGER / ADMIN REVIEW RULES
    # --------------------------------------

    if new_status == "COMPLETED":

        if current_user.role not in [
            "ADMIN",
            "MANAGER"
        ]:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Manager or Admin can approve tasks"
            )

    # --------------------------------------
    # CHANGES REQUESTED
    # --------------------------------------

    if new_status == "CHANGES_REQUESTED":

        if current_user.role not in [
            "ADMIN",
            "MANAGER"
        ]:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Manager or Admin can request changes"
            )

    # --------------------------------------
    # Update timestamps
    # --------------------------------------

    if new_status == "READY_FOR_REVIEW":

        task.submitted_at = datetime.utcnow()

    if new_status == "COMPLETED":

        task.completed_at = datetime.utcnow()

    # --------------------------------------
    # Update status
    # --------------------------------------

    task.status = new_status
    task.updated_at = datetime.utcnow()

    # --------------------------------------
    # Audit log
    # --------------------------------------

    audit = AuditLog(
        user_id=current_user.id,
        task_id=task.id,
        action="STATUS_CHANGED",
        old_value=old_status,
        new_value=new_status
    )

    db.add(audit)

    # --------------------------------------
    # Save
    # --------------------------------------

    db.commit()
    db.refresh(task)

    return task