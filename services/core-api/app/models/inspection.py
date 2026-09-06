import enum
import uuid
from datetime import datetime
from typing import List, Optional
from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Table, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InspectionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLIANT = "COMPLIANT"
    FLAGGED = "FLAGGED"
    NOTICE_ISSUED = "NOTICE_ISSUED"


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    brand_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Coordinates
    geo_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geo_lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geo_point = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)

    status: Mapped[InspectionStatus] = mapped_column(
        Enum(InspectionStatus, name="inspection_status_enum", create_type=False),
        default=InspectionStatus.PENDING,
        nullable=False,
        index=True
    )
    image_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sync_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    panels: Mapped[List["InspectionPanel"]] = relationship("InspectionPanel", back_populates="inspection", cascade="all, delete-orphan", lazy="selectin")
    violations: Mapped[List["Violation"]] = relationship("Violation", back_populates="inspection", cascade="all, delete-orphan", lazy="selectin")
