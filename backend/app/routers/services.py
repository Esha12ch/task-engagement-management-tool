from fastapi import APIRouter, Depends, HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..database import get_db
from ..dependencies import get_current_user, require_roles
from ..models import ServiceType, User
from ..schemas import (
    ServiceTypeCreate,
    ServiceTypeResponse,
    ServiceTypeUpdate
)


router = APIRouter(
    prefix="/services",
    tags=["Service Types"]
)


# ==========================================
# CREATE SERVICE TYPE
# ==========================================

@router.post(
    "/",
    response_model=ServiceTypeResponse,
    status_code=status.HTTP_201_CREATED
)
def create_service_type(
    service_data: ServiceTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    # Check duplicate service name
    existing_service = (
        db.query(ServiceType)
        .filter(ServiceType.name == service_data.name)
        .first()
    )

    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service type with this name already exists"
        )

    # Validate engagement type
    allowed_types = [
        "ONE_TIME",
        "RECURRING"
    ]

    if service_data.engagement_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Engagement type must be ONE_TIME or RECURRING"
        )

    # Create service
    service = ServiceType(
        name=service_data.name,
        description=service_data.description,
        engagement_type=service_data.engagement_type
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return service


# ==========================================
# GET ALL SERVICE TYPES
# ==========================================

@router.get(
    "/",
    response_model=list[ServiceTypeResponse]
)
def get_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    services = (
        db.query(ServiceType)
        .order_by(ServiceType.id.desc())
        .all()
    )

    return services


# ==========================================
# GET SINGLE SERVICE TYPE
# ==========================================

@router.get(
    "/{service_id}",
    response_model=ServiceTypeResponse
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

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

    return service


# ==========================================
# UPDATE SERVICE TYPE
# ==========================================

@router.put(
    "/{service_id}",
    response_model=ServiceTypeResponse
)
def update_service(
    service_id: int,
    service_data: ServiceTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

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

    # Update name
    if service_data.name is not None:

        existing_service = (
            db.query(ServiceType)
            .filter(
                ServiceType.name == service_data.name,
                ServiceType.id != service_id
            )
            .first()
        )

        if existing_service:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another service type already uses this name"
            )

        service.name = service_data.name

    # Update description
    if service_data.description is not None:
        service.description = service_data.description

    # Update engagement type
    if service_data.engagement_type is not None:

        allowed_types = [
            "ONE_TIME",
            "RECURRING"
        ]

        if service_data.engagement_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Engagement type must be ONE_TIME or RECURRING"
            )

        service.engagement_type = service_data.engagement_type

    # Update active status
    if service_data.is_active is not None:
        service.is_active = service_data.is_active

    db.commit()
    db.refresh(service)

    return service


# ==========================================
# DEACTIVATE SERVICE TYPE
# ==========================================

@router.delete(
    "/{service_id}"
)
def deactivate_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

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

    service.is_active = False

    db.commit()

    return {
        "message": "Service type deactivated successfully",
        "service_id": service.id
    }