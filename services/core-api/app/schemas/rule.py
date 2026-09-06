import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class RuleConfigurationBase(BaseModel):
    rule_set_name: str
    version: str
    is_active: bool = True
    rules_payload: Dict[str, Any]


class RuleConfigurationCreate(RuleConfigurationBase):
    pass


class RuleConfigurationUpdate(BaseModel):
    rule_set_name: Optional[str] = None
    is_active: Optional[bool] = None
    rules_payload: Optional[Dict[str, Any]] = None


class RuleConfigurationResponse(RuleConfigurationBase):
    id: uuid.UUID
    updated_by: Optional[uuid.UUID] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
