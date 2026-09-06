import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.rule_config import RuleConfiguration
from app.schemas.rule import (
    RuleConfigurationCreate,
    RuleConfigurationResponse,
    RuleConfigurationUpdate,
)
from app.security.auth import AuthUser, require_roles
from app.security.roles import UserRole
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/rules", tags=["Rules Configuration"])


@router.get("", response_model=List[RuleConfigurationResponse])
async def list_rules(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_roles([UserRole.SUPERVISOR, UserRole.ADMIN]))
):
    """Retrieves all statutory rule configurations."""
    result = await db.execute(select(RuleConfiguration).order_by(RuleConfiguration.updated_at.desc()))
    return result.scalars().all()


@router.get("/active", response_model=RuleConfigurationResponse)
async def get_active_rules(db: AsyncSession = Depends(get_db)):
    """Fetches the currently active statutory rule set."""
    result = await db.execute(select(RuleConfiguration).where(RuleConfiguration.is_active == True))
    active_rule = result.scalar_one_or_none()
    if not active_rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active rule configuration found")
    return active_rule


@router.post("", response_model=RuleConfigurationResponse, status_code=status.HTTP_201_CREATED)
async def create_rule_configuration(
    rule_in: RuleConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin endpoint to create a new statutory rule set version."""
    new_rule = RuleConfiguration(
        id=uuid.uuid4(),
        rule_set_name=rule_in.rule_set_name,
        version=rule_in.version,
        is_active=rule_in.is_active,
        rules_payload=rule_in.rules_payload,
        updated_by=current_user.id,
    )
    if rule_in.is_active:
        # Deactivate others
        await db.execute(update(RuleConfiguration).values(is_active=False))

    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)

    await log_audit_event(
        db=db,
        entity_type="RULE_CONFIG",
        entity_id=new_rule.id,
        action="RULE_SET_CREATED",
        executed_by=current_user.id,
        payload_diff={"version": rule_in.version, "rule_set_name": rule_in.rule_set_name}
    )

    return new_rule


@router.put("/{rule_id}", response_model=RuleConfigurationResponse)
async def update_rule_configuration(
    rule_id: uuid.UUID,
    rule_update: RuleConfigurationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_roles([UserRole.ADMIN]))
):
    """Admin endpoint to dynamically update thresholds, regexes, or penalties."""
    query = select(RuleConfiguration).where(RuleConfiguration.id == rule_id)
    result = await db.execute(query)
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule configuration not found")

    payload_diff = {}
    if rule_update.rule_set_name is not None:
        rule.rule_set_name = rule_update.rule_set_name
    if rule_update.rules_payload is not None:
        payload_diff["rules_payload_updated"] = True
        rule.rules_payload = rule_update.rules_payload
    if rule_update.is_active is not None and rule_update.is_active != rule.is_active:
        if rule_update.is_active:
            await db.execute(update(RuleConfiguration).values(is_active=False))
        rule.is_active = rule_update.is_active

    rule.updated_by = current_user.id
    rule.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(rule)

    await log_audit_event(
        db=db,
        entity_type="RULE_CONFIG",
        entity_id=rule.id,
        action="RULE_SET_UPDATED",
        executed_by=current_user.id,
        payload_diff=payload_diff
    )

    return rule
