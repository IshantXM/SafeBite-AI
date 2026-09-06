import uuid
from typing import Any, Dict, Optional
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DetectedField(Base):
    __tablename__ = "detected_fields"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    panel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("inspection_panels.id", ondelete="CASCADE"), nullable=False, index=True)
    field_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    extracted_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bbox_coordinates: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    measured_font_height_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    contrast_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    panel: Mapped["InspectionPanel"] = relationship("InspectionPanel", back_populates="detected_fields")
