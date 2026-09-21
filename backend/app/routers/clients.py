from fastapi import APIRouter, Depends, HTTPException, status # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..database import get_db
from ..dependencies import get_current_user, require_roles
from ..models import Client, User
from ..schemas import (
    ClientCreate,
    ClientResponse,
    ClientUpdate
)


router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)


# ==========================================
# CREATE CLIENT
# ==========================================

@router.post(
    "/",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

    # Check duplicate email
    existing_client = (
        db.query(Client)
        .filter(Client.email == client_data.email)
        .first()
    )

    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this email already exists"
        )

    # Create client
    client = Client(
        name=client_data.name,
        email=client_data.email,
        phone=client_data.phone
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


# ==========================================
# GET ALL CLIENTS
# ==========================================

@router.get(
    "/",
    response_model=list[ClientResponse]
)
def get_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    clients = (
        db.query(Client)
        .order_by(Client.id.desc())
        .all()
    )

    return clients


# ==========================================
# GET SINGLE CLIENT
# ==========================================

@router.get(
    "/{client_id}",
    response_model=ClientResponse
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

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

    return client


# ==========================================
# UPDATE CLIENT
# ==========================================

@router.put(
    "/{client_id}",
    response_model=ClientResponse
)
def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

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

    # Check email duplication if email is changed
    if client_data.email is not None:

        existing_client = (
            db.query(Client)
            .filter(
                Client.email == client_data.email,
                Client.id != client_id
            )
            .first()
        )

        if existing_client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another client already uses this email"
            )

        client.email = client_data.email

    # Update name
    if client_data.name is not None:
        client.name = client_data.name

    # Update phone
    if client_data.phone is not None:
        client.phone = client_data.phone

    # Update active status
    if client_data.is_active is not None:
        client.is_active = client_data.is_active

    db.commit()
    db.refresh(client)

    return client


# ==========================================
# DEACTIVATE CLIENT
# ==========================================

@router.delete(
    "/{client_id}"
)
def deactivate_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN")
    )
):

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

    client.is_active = False

    db.commit()

    return {
        "message": "Client deactivated successfully",
        "client_id": client.id
    }