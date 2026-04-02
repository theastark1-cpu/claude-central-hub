from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.audit_log import AuditLog


class AuditLogResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: UUID
    action: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    performed_by: str
    performed_at: datetime

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogResponse])
def list_audit_logs(
    entity_type: str | None = Query(None),
    entity_id: UUID | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        q = q.filter(AuditLog.entity_id == entity_id)
    return q.order_by(AuditLog.performed_at.desc()).offset(offset).limit(limit).all()
