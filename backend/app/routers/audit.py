from fastapi import APIRouter, Depends # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session # pyright: ignore[reportMissingImports]

from ..database import get_db
from ..dependencies import require_roles
from ..models import AuditLog, User


router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)


# ==========================================
# GET AUDIT LOGS
# ==========================================

@router.get("/")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("ADMIN", "MANAGER")
    )
):

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .all()
    )

    return logs