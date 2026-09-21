from fastapi import APIRouter, Depends, HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..database import get_db
from ..dependencies import get_current_user, require_roles
from ..models import ServiceType, TaskTemplate, User
from ..schemas import (
    TaskTemplateCreate,
    TaskTemplateResponse,
    TaskTemplateUpdate
)


router = APIRouter(
    prefix="/templates",
    tags=["Task Templates"]
)


# ==========================================
# CREATE TASK TEMPLATE
# ==========================================

@router.post(
    "/",
    response_model=TaskTemplateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_template(
    template_data: TaskTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    # Check service type exists
    service = (
        db.query(ServiceType)
        .filter(
            ServiceType.id == template_data.service_type_id
        )
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found"
        )

    # Check service is active
    if not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create template for inactive service type"
        )

    # Check duplicate template name for same service
    existing_template = (
        db.query(TaskTemplate)
        .filter(
            TaskTemplate.service_type_id
            == template_data.service_type_id,
            TaskTemplate.name == template_data.name
        )
        .first()
    )

    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task template with this name already exists for this service"
        )

    # Create template
    template = TaskTemplate(
        service_type_id=template_data.service_type_id,
        name=template_data.name,
        description=template_data.description,
        default_days=template_data.default_days,
        sequence=template_data.sequence
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template


# ==========================================
# GET ALL TASK TEMPLATES
# ==========================================

@router.get(
    "/",
    response_model=list[TaskTemplateResponse]
)
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    templates = (
        db.query(TaskTemplate)
        .order_by(
            TaskTemplate.service_type_id,
            TaskTemplate.sequence
        )
        .all()
    )

    return templates


# ==========================================
# GET TEMPLATES FOR A SERVICE
# ==========================================

@router.get(
    "/service/{service_id}",
    response_model=list[TaskTemplateResponse]
)
def get_service_templates(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check service exists
    service = (
        db.query(ServiceType)
        .filter(ServiceType.id == service_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found"
        )

    templates = (
        db.query(TaskTemplate)
        .filter(
            TaskTemplate.service_type_id == service_id,
            TaskTemplate.is_active == True
        )
        .order_by(TaskTemplate.sequence)
        .all()
    )

    return templates


# ==========================================
# GET SINGLE TASK TEMPLATE
# ==========================================

@router.get(
    "/{template_id}",
    response_model=TaskTemplateResponse
)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    template = (
        db.query(TaskTemplate)
        .filter(TaskTemplate.id == template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task template not found"
        )

    return template


# ==========================================
# UPDATE TASK TEMPLATE
# ==========================================

@router.put(
    "/{template_id}",
    response_model=TaskTemplateResponse
)
def update_template(
    template_id: int,
    template_data: TaskTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    template = (
        db.query(TaskTemplate)
        .filter(TaskTemplate.id == template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task template not found"
        )

    # Update name
    if template_data.name is not None:

        existing_template = (
            db.query(TaskTemplate)
            .filter(
                TaskTemplate.service_type_id
                == template.service_type_id,
                TaskTemplate.name
                == template_data.name,
                TaskTemplate.id != template_id
            )
            .first()
        )

        if existing_template:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another template with this name already exists"
            )

        template.name = template_data.name

    # Update description
    if template_data.description is not None:
        template.description = template_data.description

    # Update default days
    if template_data.default_days is not None:
        template.default_days = template_data.default_days

    # Update sequence
    if template_data.sequence is not None:
        template.sequence = template_data.sequence

    # Update active status
    if template_data.is_active is not None:
        template.is_active = template_data.is_active

    db.commit()
    db.refresh(template)

    return template


# ==========================================
# DEACTIVATE TASK TEMPLATE
# ==========================================

@router.delete(
    "/{template_id}"
)
def deactivate_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    template = (
        db.query(TaskTemplate)
        .filter(TaskTemplate.id == template_id)
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task template not found"
        )

    template.is_active = False

    db.commit()

    return {
        "message": "Task template deactivated successfully",
        "template_id": template.id
    }