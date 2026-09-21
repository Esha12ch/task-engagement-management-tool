from datetime import datetime, timedelta
import calendar

from fastapi import HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.exc import IntegrityError # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..models import (
    Client,
    Engagement,
    ServiceType,
    Task,
    TaskTemplate,
    User
)


# ==========================================
# CREATE ENGAGEMENT + GENERATE TASKS
# ==========================================

def create_engagement_with_tasks(
    db: Session,
    client_id: int,
    service_type_id: int,
    name: str,
    period_start: str,
    period_end: str,
    due_date: str,
    current_user: User
):

    # --------------------------------------
    # 1. Validate client
    # --------------------------------------

    client = (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create engagement for inactive client"
        )

    # --------------------------------------
    # 2. Validate service type
    # --------------------------------------

    service = (
        db.query(ServiceType)
        .filter(ServiceType.id == service_type_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found"
        )

    if not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create engagement for inactive service type"
        )

    # --------------------------------------
    # 3. Convert dates
    # --------------------------------------

    try:
        start_date = datetime.strptime(
            period_start,
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            period_end,
            "%Y-%m-%d"
        ).date()

        engagement_due_date = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dates must use YYYY-MM-DD format"
        )

    # --------------------------------------
    # 4. Validate date order
    # --------------------------------------

    if start_date > end_date:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period start date cannot be after period end date"
        )

    if engagement_due_date < start_date:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date cannot be before period start date"
        )

    # --------------------------------------
    # 5. Prevent duplicate engagement
    # --------------------------------------

    existing_engagement = (
        db.query(Engagement)
        .filter(
            Engagement.client_id == client_id,
            Engagement.service_type_id == service_type_id,
            Engagement.period_start == start_date,
            Engagement.period_end == end_date
        )
        .first()
    )

    if existing_engagement:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An engagement already exists for this client, service, and period"
        )

    # --------------------------------------
    # 6. Get active task templates
    # --------------------------------------

    templates = (
        db.query(TaskTemplate)
        .filter(
            TaskTemplate.service_type_id == service_type_id,
            TaskTemplate.is_active == True
        )
        .order_by(TaskTemplate.sequence)
        .all()
    )

    if not templates:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active task templates found for this service type"
        )

    # --------------------------------------
    # 7. Create engagement
    # --------------------------------------

    engagement = Engagement(
        client_id=client_id,
        service_type_id=service_type_id,
        name=name,
        period_start=start_date,
        period_end=end_date,
        due_date=engagement_due_date,
        status="OPEN"
    )

    db.add(engagement)
    db.flush()

    # --------------------------------------
    # 8. Automatically generate tasks
    # --------------------------------------

    for template in templates:

        task_due_date = start_date + timedelta(
            days=template.default_days
        )

        # Don't allow task deadline beyond
        # engagement deadline
        if task_due_date > engagement_due_date:
            task_due_date = engagement_due_date

        task = Task(
            engagement_id=engagement.id,
            assigned_to_id=None,
            created_by_id=current_user.id,
            title=template.name,
            description=template.description,
            status="NOT_STARTED",
            due_date=task_due_date
        )

        db.add(task)

    # --------------------------------------
    # 9. Commit everything together
    # --------------------------------------

    try:

        db.commit()

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate engagement already exists"
        )

    # --------------------------------------
    # 10. Refresh engagement
    # --------------------------------------

    db.refresh(engagement)

    return engagement
def generate_next_period(db, engagement):
    """
    Generate the next period for a recurring engagement.

    Example:
    September 2026
    -> October 2026
    """

    from datetime import date
    import calendar

    if engagement.service_type.engagement_type != "RECURRING":
        raise ValueError(
            "Only recurring services can generate the next period."
        )

    current_start = engagement.period_start
    current_end = engagement.period_end

    # Move to the next month
    if current_start.month == 12:
        next_year = current_start.year + 1
        next_month = 1
    else:
        next_year = current_start.year
        next_month = current_start.month + 1

    next_start = date(
        next_year,
        next_month,
        1
    )

    last_day = calendar.monthrange(
        next_year,
        next_month
    )[1]

    next_end = date(
        next_year,
        next_month,
        last_day
    )

    # Keep the same duration/relative due date pattern
    days_until_due = (
        engagement.due_date - engagement.period_start
    ).days

    next_due_date = next_start.replace()

    from datetime import timedelta

    next_due_date = (
        next_start +
        timedelta(days=days_until_due)
    )

    # Do not allow due date after period end
    if next_due_date > next_end:
        next_due_date = next_end

    # Prevent duplicate next-period engagement
    existing = (
        db.query(Engagement)
        .filter(
            Engagement.client_id ==
            engagement.client_id,

            Engagement.service_type_id ==
            engagement.service_type_id,

            Engagement.period_start ==
            next_start,

            Engagement.period_end ==
            next_end
        )
        .first()
    )

    if existing:
        raise ValueError(
            "Next period engagement already exists."
        )

    # Get active templates
    templates = (
        db.query(TaskTemplate)
        .filter(
            TaskTemplate.service_type_id ==
            engagement.service_type_id,

            TaskTemplate.is_active == True
        )
        .order_by(TaskTemplate.sequence)
        .all()
    )

    if not templates:
        raise ValueError(
            "No active task templates found."
        )

    # Create next engagement
    next_engagement = Engagement(
        client_id=engagement.client_id,
        service_type_id=engagement.service_type_id,
        name=(
            f"{engagement.client.name} - "
            f"{next_start.strftime('%B %Y')} "
            f"{engagement.service_type.name}"
        ),
        period_start=next_start,
        period_end=next_end,
        due_date=next_due_date,
        status="OPEN"
    )

    db.add(next_engagement)
    db.flush()

    # Generate tasks from templates
    for template in templates:

        task_due_date = (
            next_start +
            timedelta(days=template.default_days)
        )

        if task_due_date > next_due_date:
            task_due_date = next_due_date

        task = Task(
            engagement_id=next_engagement.id,
            assigned_to_id=None,
            created_by_id=engagement.created_by_id,
            title=template.name,
            description=template.description,
            status="NOT_STARTED",
            due_date=task_due_date
        )

        db.add(task)

    db.commit()
    db.refresh(next_engagement)

    return next_engagement