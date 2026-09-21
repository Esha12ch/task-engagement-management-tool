from fastapi import APIRouter, Depends, HTTPException  # type: ignore
from sqlalchemy.orm import Session  # type: ignore

from ..database import get_db
from ..models import User, UserRole
from ..auth import hash_password
from ..dependencies import require_roles


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# =========================
# GET ALL USERS
# ADMIN ONLY
# =========================

@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    users = (
        db.query(User)
        .order_by(User.id)
        .all()
    )

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


# =========================
# GET TEAM MEMBERS
# ADMIN + MANAGER
# =========================

@router.get("/team-members")
def get_team_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.MANAGER
        )
    )
):

    team_members = (
        db.query(User)
        .filter(
            User.role == UserRole.TEAM_MEMBER,
            User.is_active == True
        )
        .order_by(User.id)
        .all()
    )

    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        }
        for user in team_members
    ]


# =========================
# CREATE USER
# ADMIN ONLY
# =========================

@router.post("/")
def create_user(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    name = user_data.get("name")
    email = user_data.get("email")
    password = user_data.get("password")
    role = user_data.get("role")

    if not name or not email or not password or not role:
        raise HTTPException(
            status_code=400,
            detail="Name, email, password and role are required"
        )

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )

    try:
        user_role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    new_user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=user_role,
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "role": new_user.role,
            "is_active": new_user.is_active
        }
    }


# =========================
# UPDATE USER
# ADMIN ONLY
# =========================

@router.put("/{user_id}")
def update_user(
    user_id: int,
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if "name" in user_data:
        user.name = user_data["name"]

    if "email" in user_data:

        existing_user = (
            db.query(User)
            .filter(
                User.email == user_data["email"],
                User.id != user_id
            )
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

        user.email = user_data["email"]

    if "role" in user_data:

        try:
            user.role = UserRole(
                user_data["role"]
            )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid role"
            )

    if (
        "password" in user_data
        and user_data["password"]
    ):

        user.password_hash = hash_password(
            user_data["password"]
        )

    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active
        }
    }


# =========================
# DEACTIVATE USER
# ADMIN ONLY
# =========================

@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )

    user.is_active = False

    db.commit()

    return {
        "message": "User deactivated successfully"
    }


# =========================
# ACTIVATE USER
# ADMIN ONLY
# =========================

@router.put("/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.is_active = True

    db.commit()

    return {
        "message": "User activated successfully"
    }