import uuid

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    performed_by: str = "system",
    metadata: dict | None = None,
):
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        performed_by=performed_by,
        metadata_=metadata,
    )
    db.add(entry)
