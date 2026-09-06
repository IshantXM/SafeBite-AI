import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ViolationSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


class ViolationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RESOLVED = "RESOLVED"
    APPEALED = "APPEALED"


class Violation(Base):
    __tablename__ = "violations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    clause_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[ViolationSeverity] = mapped_column(
        Enum(ViolationSeverity, name="violation_severity_enum", create_type=False),
        default=ViolationSeverity.HIGH,
        nullable=False
    )
    ai_detected: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    human_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    penalty_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("25000.00"), nullable=False)
    status: Mapped[ViolationStatus] = mapped_column(
        Enum(ViolationStatus, name="violation_status_enum", create_type=False),
        default=ViolationStatus.ACTIVE,
        nullable=False,
        index=True
    )
    override_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="violations")
