import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.violation import ViolationSeverity, ViolationStatus


class ViolationBase(BaseModel):
    rule_id: str
    clause_reference: str
    description: Optional[str] = None
    severity: ViolationSeverity = ViolationSeverity.HIGH
    ai_detected: bool = True
    penalty_amount: Decimal = Decimal("25000.00")
    status: ViolationStatus = ViolationStatus.ACTIVE


class ViolationCreate(ViolationBase):
    pass


class ViolationUpdate(BaseModel):
    status: Optional[ViolationStatus] = None
    human_override: Optional[bool] = None
    override_reason: Optional[str] = None
    penalty_amount: Optional[Decimal] = None


class ViolationResponse(ViolationBase):
    id: uuid.UUID
    inspection_id: uuid.UUID
    human_override: bool
    override_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
