import uuid
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog


async def log_audit_event(
    db: AsyncSession,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    executed_by: uuid.UUID,
    payload_diff: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """Appends an immutable entry to the audit_logs table."""
    audit_entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        executed_by=executed_by,
        payload_diff=payload_diff
    )
    db.add(audit_entry)
    await db.flush()
    return audit_entry
