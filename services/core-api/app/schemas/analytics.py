from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [lng, lat]


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class RepeatOffenderItem(BaseModel):
    brand_name: str
    category: Optional[str] = None
    violation_count: int
    total_penalties_inr: float
    common_violations: List[str]


class RepeatOffendersResponse(BaseModel):
    total_offenders: int
    offenders: List[RepeatOffenderItem]
