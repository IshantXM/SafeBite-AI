export type InspectionStatus = 'PENDING' | 'COMPLIANT' | 'FLAGGED' | 'NOTICE_ISSUED';
export type PanelType = 'FRONT' | 'BACK' | 'SIDE' | 'TOP' | 'BOTTOM';
export type ViolationSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM';
export type ViolationStatus = 'ACTIVE' | 'RESOLVED' | 'APPEALED';

export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface DetectedField {
  id: string;
  panel_id: string;
  field_key: string;
  extracted_value?: string;
  confidence?: number;
  bbox_coordinates?: {
    bbox?: [number, number, number, number];
    polygon?: number[][];
  };
  measured_font_height_mm?: number;
  contrast_ratio?: number;
}

export interface Violation {
  id: string;
  inspection_id: string;
  rule_id: string;
  clause_reference: string;
  description?: string;
  severity: ViolationSeverity;
  ai_detected: boolean;
  human_override: boolean;
  penalty_amount: number;
  status: ViolationStatus;
  override_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface InspectionPanel {
  id: string;
  panel_type: PanelType;
  raw_image_url: string;
  processed_image_url?: string;
  calibration_ratio_px_mm?: number;
  detected_fields: DetectedField[];
}

export interface Inspection {
  id: string;
  inspector_id: string;
  barcode?: string;
  brand_name?: string;
  category?: string;
  geo_lat?: number;
  geo_lng?: number;
  status: InspectionStatus;
  image_sha256: string;
  sync_timestamp: string;
  created_at: string;
  updated_at: string;
  panels: InspectionPanel[];
  violations: Violation[];
}

export interface AnalyticsSummary {
  total_inspections: number;
  pending_reviews: number;
  flagged_cases: number;
  notices_issued: number;
  compliant_cases: number;
  violation_rate_pct: number;
  total_penalties_assessed_inr: number;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [lng, lat]
  };
  properties: {
    id: string;
    brand_name: string;
    category: string;
    status: InspectionStatus;
    violation_count: number;
    sync_timestamp: string;
  };
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

export interface RepeatOffender {
  brand_name: string;
  category?: string;
  violation_count: number;
  total_penalties_inr: number;
  common_violations: string[];
}

export interface RuleConfiguration {
  id: string;
  rule_set_name: string;
  version: string;
  is_active: boolean;
  rules_payload: any;
  updated_by?: string;
  updated_at: string;
}
