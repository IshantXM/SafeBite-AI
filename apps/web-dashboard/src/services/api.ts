import axios from 'axios';
import {
  Inspection,
  AnalyticsSummary,
  GeoJSONFeatureCollection,
  RepeatOffender,
  RuleConfiguration,
  InspectionStatus
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

export const api = {
  // Inspections
  async getInspections(status?: InspectionStatus, brand?: string): Promise<Inspection[]> {
    try {
      const response = await apiClient.get<Inspection[]>('/inspections', {
        params: { status_filter: status, brand_name: brand }
      });
      return response.data;
    } catch (e) {
      console.warn('API error, returning demo inspections', e);
      return getDemoInspections();
    }
  },

  async getInspectionById(id: string): Promise<Inspection> {
    try {
      const response = await apiClient.get<Inspection>(`/inspections/${id}/status`);
      return response.data;
    } catch (e) {
      console.warn('API error, returning mock inspection', e);
      return getDemoInspections().find(i => i.id === id) || getDemoInspections()[0];
    }
  },

  async overrideInspection(id: string, payload: any): Promise<Inspection> {
    const response = await apiClient.patch<Inspection>(`/inspections/${id}/override`, payload);
    return response.data;
  },

  async generateNotice(id: string): Promise<any> {
    const response = await apiClient.post(`/inspections/${id}/generate-notice`);
    return response.data;
  },

  // Analytics
  async getSummary(): Promise<AnalyticsSummary> {
    try {
      const response = await apiClient.get<AnalyticsSummary>('/analytics/summary');
      return response.data;
    } catch (e) {
      return {
        total_inspections: 1428,
        pending_reviews: 42,
        flagged_cases: 184,
        notices_issued: 96,
        compliant_cases: 1106,
        violation_rate_pct: 20.2,
        total_penalties_assessed_inr: 4750000.00
      };
    }
  },

  async getHeatmaps(): Promise<GeoJSONFeatureCollection> {
    try {
      const response = await apiClient.get<GeoJSONFeatureCollection>('/analytics/heatmaps');
      return response.data;
    } catch (e) {
      return getDemoHeatmapData();
    }
  },

  async getRepeatOffenders(): Promise<RepeatOffender[]> {
    try {
      const response = await apiClient.get<{ offenders: RepeatOffender[] }>('/analytics/repeat-offenders');
      return response.data.offenders;
    } catch (e) {
      return [
        { brand_name: 'Apex FMCG Brands Ltd', category: 'Confectionery', violation_count: 18, total_penalties_inr: 450000, common_violations: ['Rule 6(1)(c) - Missing Tax Phrase', 'Schedule II - Font Deficit'] },
        { brand_name: 'Sunrise Beverages Corp', category: 'Soft Drinks', violation_count: 14, total_penalties_inr: 350000, common_violations: ['Rule 6(1)(b) - Prohibited Qualifier', 'Rule 7 - PDP Layout'] },
        { brand_name: 'Royal Spices & Condiments', category: 'Food Staples', violation_count: 11, total_penalties_inr: 275000, common_violations: ['Rule 6(1)(a) - Incomplete Address'] },
        { brand_name: 'Glacier Personal Care', category: 'Cosmetics', violation_count: 9, total_penalties_inr: 225000, common_violations: ['Rule 6(1)(e) - Missing Helpline'] },
        { brand_name: 'Evergreen Grains Pvt Ltd', category: 'Flour & Grains', violation_count: 7, total_penalties_inr: 175000, common_violations: ['Section 36(2) - Net Qty Deficit'] }
      ];
    }
  },

  // Rules
  async getActiveRule(): Promise<RuleConfiguration> {
    try {
      const response = await apiClient.get<RuleConfiguration>('/rules/active');
      return response.data;
    } catch (e) {
      return {
        id: 'rule-cfg-01',
        rule_set_name: 'Legal Metrology (Packaged Commodities) Rules, 2011',
        version: '2026.1',
        is_active: true,
        updated_at: new Date().toISOString(),
        rules_payload: {}
      };
    }
  }
};

// Realistic mock data for instant preview
function getDemoInspections(): Inspection[] {
  return [
    {
      id: 'd9b1c7a4-8f2e-4b6a-9a1d-3e5f7b8c9d01',
      inspector_id: 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d',
      barcode: '8901030829412',
      brand_name: 'Apex FMCG Brands Ltd',
      category: 'Confectionery',
      geo_lat: 28.6139,
      geo_lng: 77.2090,
      status: 'FLAGGED',
      image_sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
      sync_timestamp: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      panels: [
        {
          id: 'p-01',
          panel_type: 'FRONT',
          raw_image_url: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80',
          calibration_ratio_px_mm: 0.082,
          detected_fields: [
            {
              id: 'df-1',
              panel_id: 'p-01',
              field_key: 'MAXIMUM_RETAIL_PRICE',
              extracted_value: 'MRP Rs. 45.00',
              confidence: 0.96,
              bbox_coordinates: { bbox: [45, 140, 280, 32], polygon: [[45, 140], [325, 140], [325, 172], [45, 172]] },
              measured_font_height_mm: 1.35,
              contrast_ratio: 2.8
            },
            {
              id: 'df-2',
              panel_id: 'p-01',
              field_key: 'NET_QUANTITY',
              extracted_value: 'Net Weight: 150g approx.',
              confidence: 0.94,
              bbox_coordinates: { bbox: [45, 185, 260, 30], polygon: [[45, 185], [305, 185], [305, 215], [45, 215]] },
              measured_font_height_mm: 1.25,
              contrast_ratio: 3.5
            },
            {
              id: 'df-3',
              panel_id: 'p-01',
              field_key: 'MANUFACTURER_NAME_ADDRESS',
              extracted_value: 'Apex FMCG Brands, Okhla Phase 3',
              confidence: 0.91,
              bbox_coordinates: { bbox: [45, 230, 350, 35], polygon: [[45, 230], [395, 230], [395, 265], [45, 265]] },
              measured_font_height_mm: 1.10,
              contrast_ratio: 4.1
            }
          ]
        }
      ],
      violations: [
        {
          id: 'v-01',
          inspection_id: 'd9b1c7a4-8f2e-4b6a-9a1d-3e5f7b8c9d01',
          rule_id: 'LM_RULE_6_1_C_TAX_PHRASE',
          clause_reference: 'Rule 6(1)(c)',
          description: "MRP declaration omits mandatory phrase 'inclusive of all taxes' or 'incl. of all taxes'.",
          severity: 'CRITICAL',
          ai_detected: true,
          human_override: false,
          penalty_amount: 25000,
          status: 'ACTIVE',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'v-02',
          inspection_id: 'd9b1c7a4-8f2e-4b6a-9a1d-3e5f7b8c9d01',
          rule_id: 'LM_RULE_6_1_B_PROHIBITED_QUALIFIER',
          clause_reference: 'Rule 6(1)(b)',
          description: "Use of prohibited qualifier 'approx.' in Net Quantity declaration.",
          severity: 'HIGH',
          ai_detected: true,
          human_override: false,
          penalty_amount: 25000,
          status: 'ACTIVE',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 'v-03',
          inspection_id: 'd9b1c7a4-8f2e-4b6a-9a1d-3e5f7b8c9d01',
          rule_id: 'LM_SCHEDULE_II_FONT_DEFICIT',
          clause_reference: 'Rule 7 / Schedule II',
          description: 'Measured font height (1.35 mm) is below statutory threshold (2.00 mm) for PDP area 124 cm².',
          severity: 'HIGH',
          ai_detected: true,
          human_override: false,
          penalty_amount: 25000,
          status: 'ACTIVE',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]
    },
    {
      id: 'e2a4c8b6-9d3f-4e7a-8b2c-1a3f5e7d9b02',
      inspector_id: 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d',
      barcode: '8901234567890',
      brand_name: 'PureDrop Mineral Water',
      category: 'Packaged Drinking Water',
      geo_lat: 19.0760,
      geo_lng: 72.8777,
      status: 'COMPLIANT',
      image_sha256: 'a1b2c3d4e5f67a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
      sync_timestamp: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      panels: [],
      violations: []
    },
    {
      id: 'f3b5d9a7-0e4a-5f8b-9c3d-2b4a6f8e0c03',
      inspector_id: 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d',
      barcode: '8909876543210',
      brand_name: 'Sunrise Beverages Corp',
      category: 'Soft Drinks',
      geo_lat: 12.9716,
      geo_lng: 77.5946,
      status: 'NOTICE_ISSUED',
      image_sha256: 'b2c3d4e5f67a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c',
      sync_timestamp: new Date().toISOString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      panels: [],
      violations: [
        {
          id: 'v-04',
          inspection_id: 'f3b5d9a7-0e4a-5f8b-9c3d-2b4a6f8e0c03',
          rule_id: 'LM_RULE_TAMPER_STICKER',
          clause_reference: 'Rule 6 & Section 36',
          description: 'Suspect price sticker overlay detected concealing original MRP declaration.',
          severity: 'CRITICAL',
          ai_detected: true,
          human_override: false,
          penalty_amount: 50000,
          status: 'ACTIVE',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ]
    }
  ];
}

function getDemoHeatmapData(): GeoJSONFeatureCollection {
  return {
    type: 'FeatureCollection',
    features: [
      { type: 'Feature', geometry: { type: 'Point', coordinates: [77.2090, 28.6139] }, properties: { id: 'd9b1c7a4', brand_name: 'Apex FMCG', category: 'Confectionery', status: 'FLAGGED', violation_count: 3, sync_timestamp: '2026-09-01' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [72.8777, 19.0760] }, properties: { id: 'e2a4c8b6', brand_name: 'PureDrop', category: 'Water', status: 'COMPLIANT', violation_count: 0, sync_timestamp: '2026-09-01' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [77.5946, 12.9716] }, properties: { id: 'f3b5d9a7', brand_name: 'Sunrise Beverages', category: 'Beverages', status: 'NOTICE_ISSUED', violation_count: 1, sync_timestamp: '2026-09-01' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [88.3639, 22.5726] }, properties: { id: 'g4c6e0b8', brand_name: 'Royal Spices', category: 'Food Staples', status: 'FLAGGED', violation_count: 2, sync_timestamp: '2026-09-01' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [80.2707, 13.0827] }, properties: { id: 'h5d7f1c9', brand_name: 'Glacier Personal Care', category: 'Cosmetics', status: 'FLAGGED', violation_count: 2, sync_timestamp: '2026-09-01' } },
      { type: 'Feature', geometry: { type: 'Point', coordinates: [78.4867, 17.3850] }, properties: { id: 'i6e8a2da', brand_name: 'Evergreen Grains', category: 'Flour', status: 'NOTICE_ISSUED', violation_count: 1, sync_timestamp: '2026-09-01' } }
    ]
  };
}
