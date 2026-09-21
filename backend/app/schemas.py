from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field  # type: ignore[import-not-found]


# ==========================================
# AUTH SCHEMAS
# ==========================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# ==========================================
# CLIENT SCHEMAS
# ==========================================

class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = None


class ClientUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool | None = None


class ClientResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    is_active: bool

    class Config:
        from_attributes = True

# ==========================================
# SERVICE TYPE SCHEMAS
# ==========================================

class ServiceTypeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None
    engagement_type: str


class ServiceTypeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    description: str | None = None
    engagement_type: str | None = None
    is_active: bool | None = None


class ServiceTypeResponse(BaseModel):
    id: int
    name: str
    description: str | None
    engagement_type: str
    is_active: bool

    class Config:
        from_attributes = True

# ==========================================
# TASK TEMPLATE SCHEMAS
# ==========================================

class TaskTemplateCreate(BaseModel):
    service_type_id: int
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    default_days: int = Field(default=1, ge=1)
    sequence: int = Field(default=1, ge=1)


class TaskTemplateUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )
    description: str | None = None
    default_days: int | None = Field(
        default=None,
        ge=1
    )
    sequence: int | None = Field(
        default=None,
        ge=1
    )
    is_active: bool | None = None


class TaskTemplateResponse(BaseModel):
    id: int
    service_type_id: int
    name: str
    description: str | None
    default_days: int
    sequence: int
    is_active: bool

    class Config:
        from_attributes = True

    # ==========================================
# ENGAGEMENT SCHEMAS
# ==========================================

class EngagementCreate(BaseModel):
    client_id: int
    service_type_id: int
    name: str = Field(min_length=2, max_length=150)
    period_start: str
    period_end: str
    due_date: str
    
class EngagementUpdate(BaseModel):
    name: str
    period_start: date
    period_end: date
    due_date: date
    status: str

class EngagementResponse(BaseModel):
    id: int
    client_id: int
    service_type_id: int
    name: str
    period_start: date
    period_end: date
    due_date: date
    status: str

    class Config:
        from_attributes = True



# ==========================================
# TASK SCHEMAS
# ==========================================

class TaskAssignRequest(BaseModel):
    assigned_to_id: int


class TaskStatusUpdate(BaseModel):
    status: str


class TaskResponse(BaseModel):
    id: int
    engagement_id: int
    assigned_to_id: int | None
    created_by_id: int
    title: str
    description: str | None
    status: str
    due_date: date | None
    submitted_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True