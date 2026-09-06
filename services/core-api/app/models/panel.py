import enum
import uuid
from typing import List, Optional
from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PanelType(str, enum.Enum):
    FRONT = "FRONT"
    BACK = "BACK"
    SIDE = "SIDE"
    TOP = "TOP"
    BOTTOM = "BOTTOM"


class InspectionPanel(Base):
    __tablename__ = "inspection_panels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    panel_type: Mapped[PanelType] = mapped_column(
        Enum(PanelType, name="panel_type_enum", create_type=False),
        default=PanelType.FRONT,
        nullable=False
    )
    raw_image_url: Mapped[str] = mapped_column(Text, nullable=False)
    processed_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calibration_ratio_px_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="panels")
    detected_fields: Mapped[List["DetectedField"]] = relationship("DetectedField", back_populates="panel", cascade="all, delete-orphan", lazy="selectin")
