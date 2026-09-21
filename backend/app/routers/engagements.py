from fastapi import APIRouter, Depends, HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..database import get_db
from ..dependencies import get_current_user, require_roles
from ..models import Engagement, Task, User
from ..schemas import (
    EngagementCreate,
    EngagementUpdate,
    EngagementResponse
)
from ..services.engagement_service import (
    create_engagement_with_tasks,
    generate_next_period
)


router = APIRouter(
    prefix="/engagements",
    tags=["Engagements"]
)


# ==========================================
# CREATE ENGAGEMENT
# ==========================================

@router.post(
    "/",
    response_model=EngagementResponse,
    status_code=status.HTTP_201_CREATED
)
def create_engagement(
    engagement_data: EngagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    )
):

    engagement = create_engagement_with_tasks(
        db=db,
        client_id=engagement_data.client_id,
        service_type_id=engagement_data.service_type_id,
        name=engagement_data.name,
        period_start=engagement_data.period_start,
        period_end=engagement_data.period_end,
        due_date=engagement_data.due_date,
        current_user=current_user
    )

    return engagement


# ==========================================
# GET ALL ENGAGEMENTS
# ==========================================

@router.get(
    "/",
    response_model=list[EngagementResponse]
)
def get_engagements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    engagements = (
        db.query(Engagement)
        .order_by(Engagement.id.desc())
        .all()
    )

    return engagements


# ==========================================
# GET SINGLE ENGAGEMENT
# ==========================================

@router.get(
    "/{engagement_id}",
    response_model=EngagementResponse
)
def get_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    engagement = (
        db.query(Engagement)
        .filter(
            Engagement.id == engagement_id
        )
        .first()
    )

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )

    return engagement


# ==========================================
# GET TASKS FOR ENGAGEMENT
# ==========================================

@router.get(
    "/{engagement_id}/tasks"
)
def get_engagement_tasks(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check engagement exists
    engagement = (
        db.query(Engagement)
        .filter(
            Engagement.id == engagement_id
        )
        .first()
    )

    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )

    tasks = (
        db.query(Task)
        .filter(
            Task.engagement_id == engagement_id
        )
        .order_by(Task.id)
        .all()
    )

    return tasks
@router.post("/{engagement_id}/generate-next")
def generate_next_engagement(
    engagement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER"
        )
    )
):
    engagement = (
        db.query(Engagement)
        .filter(
            Engagement.id == engagement_id
        )
        .first()
    )

    if not engagement:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found"
        )

    try:
        next_engagement = generate_next_period(
            db,
            engagement
        )

        return {
            "message": "Next recurring period generated successfully",
            "engagement_id": next_engagement.id,
            "name": next_engagement.name,
            "period_start": next_engagement.period_start,
            "period_end": next_engagement.period_end,
            "due_date": next_engagement.due_date
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.put("/{engagement_id}")
def update_engagement(
    engagement_id: int,
    data: EngagementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "ADMIN",
            "MANAGER"
        )
    )
):
    engagement = (
        db.query(Engagement)
        .filter(
            Engagement.id == engagement_id
        )
        .first()
    )

    if not engagement:
        raise HTTPException(
            status_code=404,
            detail="Engagement not found"
        )

    # Validate dates
    if data.period_start > data.period_end:
        raise HTTPException(
            status_code=400,
            detail="Period start cannot be after period end."
        )

    if data.due_date < data.period_start:
        raise HTTPException(
            status_code=400,
            detail="Due date cannot be before period start."
        )

    if data.due_date > data.period_end:
        raise HTTPException(
            status_code=400,
            detail="Due date cannot be after period end."
        )

    # Validate status
    allowed_statuses = [
        "OPEN",
        "IN_PROGRESS",
        "COMPLETED",
        "CLOSED"
    ]

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid engagement status."
        )

    engagement.name = data.name
    engagement.period_start = data.period_start
    engagement.period_end = data.period_end
    engagement.due_date = data.due_date
    engagement.status = data.status

    db.commit()
    db.refresh(engagement)

    return engagement