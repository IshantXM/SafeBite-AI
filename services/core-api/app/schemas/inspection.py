import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.inspection import InspectionStatus
from app.models.panel import PanelType
from app.schemas.violation import ViolationResponse


class DetectedFieldResponse(BaseModel):
    id: uuid.UUID
    panel_id: uuid.UUID
    field_key: str
    extracted_value: Optional[str] = None
    confidence: Optional[float] = None
    bbox_coordinates: Optional[Dict[str, Any]] = None
    measured_font_height_mm: Optional[float] = None
    contrast_ratio: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class InspectionPanelResponse(BaseModel):
    id: uuid.UUID
    panel_type: PanelType
    raw_image_url: str
    processed_image_url: Optional[str] = None
    calibration_ratio_px_mm: Optional[float] = None
    detected_fields: List[DetectedFieldResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InspectionIngestResponse(BaseModel):
    job_id: uuid.UUID
    inspection_id: uuid.UUID
    status: str
    message: str


class InspectionStatusResponse(BaseModel):
    id: uuid.UUID
    inspector_id: uuid.UUID
    barcode: Optional[str] = None
    brand_name: Optional[str] = None
    category: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None
    status: InspectionStatus
    image_sha256: str
    sync_timestamp: datetime
    created_at: datetime
    updated_at: datetime
    panels: List[InspectionPanelResponse] = []
    violations: List[ViolationResponse] = []

    model_config = ConfigDict(from_attributes=True)


class InspectionOverrideRequest(BaseModel):
    status: Optional[InspectionStatus] = None
    brand_name: Optional[str] = None
    barcode: Optional[str] = None
    violations_override: Optional[List[Dict[str, Any]]] = None
    override_notes: str
