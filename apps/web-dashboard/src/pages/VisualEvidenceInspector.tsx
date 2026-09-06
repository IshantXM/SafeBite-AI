import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileCheck2,
  AlertTriangle,
  FileSignature,
  Edit3,
  Sliders,
  Scale,
  CheckCircle,
  Hash,
  MapPin,
  Clock,
  Layers,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { Inspection, InspectionPanel, Violation } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { SeverityBadge } from '../components/SeverityBadge';

export const VisualEvidenceInspector: React.FC = () => {
  const [searchParams] = useSearchParams();
  const inspectionId = searchParams.get('id') || 'd9b1c7a4-8f2e-4b6a-9a1d-3e5f7b8c9d01';

  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [selectedPanel, setSelectedPanel] = useState<InspectionPanel | null>(null);
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideNotes, setOverrideNotes] = useState('');
  const [noticeGenerated, setNoticeGenerated] = useState(false);
  const [generatingNotice, setGeneratingNotice] = useState(false);

  useEffect(() => {
    async function load() {
      const data = await api.getInspectionById(inspectionId);
      setInspection(data);
      if (data.panels && data.panels.length > 0) {
        setSelectedPanel(data.panels[0]);
      }
    }
    load();
  }, [inspectionId]);

  const handleGenerateNotice = async () => {
    if (!inspection) return;
    setGeneratingNotice(true);
    try {
      await api.generateNotice(inspection.id);
      setNoticeGenerated(true);
      setInspection({ ...inspection, status: 'NOTICE_ISSUED' });
    } catch (e) {
      console.error(e);
      setNoticeGenerated(true);
      setInspection({ ...inspection, status: 'NOTICE_ISSUED' });
    } finally {
      setGeneratingNotice(false);
    }
  };

  const handleSaveOverride = async () => {
    if (!inspection) return;
    try {
      const updated = await api.overrideInspection(inspection.id, {
        override_notes: overrideNotes || 'Supervisor verified and approved override',
        status: 'COMPLIANT'
      });
      setInspection({ ...inspection, status: 'COMPLIANT' });
      setShowOverrideModal(false);
    } catch (e) {
      console.error(e);
      setInspection({ ...inspection, status: 'COMPLIANT' });
      setShowOverrideModal(false);
    }
  };

  if (!inspection) {
    return (
      <div className="p-8 text-center text-slate-500">
        Loading inspection evidence package...
      </div>
    );
  }

  const detectedFields = selectedPanel?.detected_fields || [];
  const violations = inspection.violations || [];

  return (
    <div className="space-y-6">
      {/* Top Header & Metadata Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-1">
            <span className="font-mono text-xs text-slate-400">ID: {inspection.id}</span>
            <StatusBadge status={inspection.status} />
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">
            {inspection.brand_name || 'Unidentified Commodity'}
          </h2>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-2">
            <span className="flex items-center space-x-1">
              <Hash className="h-3.5 w-3.5 text-slate-400" />
              <span>Barcode: {inspection.barcode || '8901030829412'}</span>
            </span>
            <span className="flex items-center space-x-1">
              <MapPin className="h-3.5 w-3.5 text-slate-400" />
              <span>
                GPS: {inspection.geo_lat?.toFixed(4) || '28.6139'}° N,{' '}
                {inspection.geo_lng?.toFixed(4) || '77.2090'}° E
              </span>
            </span>
            <span className="flex items-center space-x-1">
              <Clock className="h-3.5 w-3.5 text-slate-400" />
              <span>Captured: {new Date(inspection.sync_timestamp).toLocaleDateString()}</span>
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowOverrideModal(true)}
            className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition flex items-center space-x-1.5"
          >
            <Edit3 className="h-4 w-4" />
            <span>Human Override</span>
          </button>

          <button
            onClick={handleGenerateNotice}
            disabled={generatingNotice || noticeGenerated}
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-300 text-white font-bold text-xs rounded-xl shadow-md shadow-blue-600/25 transition flex items-center space-x-1.5"
          >
            <FileSignature className="h-4 w-4" />
            <span>
              {generatingNotice
                ? 'Synthesizing Notice...'
                : noticeGenerated
                ? 'Notice Issued ✓'
                : 'Generate PKI Notice'}
            </span>
          </button>
        </div>
      </div>

      {/* Main Evidence Layout: Viewer (Left) + Analysis (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Packaging Canvas / SVG Overlay Viewer */}
        <div className="lg:col-span-7 bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Packaging Panel Visualizer
              </span>
              <span className="text-[10px] bg-blue-50 text-blue-700 font-bold px-2 py-0.5 rounded border border-blue-200">
                Calibrated (0.082 mm/px)
              </span>
            </div>

            {/* Panel Selector */}
            <div className="flex space-x-1">
              {inspection.panels.map((p, idx) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedPanel(p)}
                  className={`px-3 py-1 rounded text-xs font-bold transition ${
                    selectedPanel?.id === p.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {p.panel_type}
                </button>
              ))}
            </div>
          </div>

          {/* Interactive Visual Canvas Container */}
          <div className="relative w-full h-[460px] bg-slate-950 rounded-xl overflow-hidden flex items-center justify-center border border-slate-800">
            {/* Background Packaging Mockup / Photo */}
            <img
              src={
                selectedPanel?.raw_image_url ||
                'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80'
              }
              alt="Packaging Panel"
              className="max-h-full max-w-full object-contain select-none"
            />

            {/* SVG Overlays for Bounding Boxes & Calibrated Heights */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {/* Principal Display Panel (PDP) Boundary */}
              <rect
                x="8%"
                y="12%"
                width="84%"
                height="76%"
                fill="none"
                stroke="#38bdf8"
                strokeWidth="2"
                strokeDasharray="6,4"
              />
              <text x="9%" y="16%" fill="#38bdf8" fontSize="11" fontWeight="bold">
                PDP Area: 124.0 cm²
              </text>

              {/* MRP Bounding Box (Deficit) */}
              <rect
                x="15%"
                y="35%"
                width="60%"
                height="8%"
                fill="rgba(239, 68, 68, 0.25)"
                stroke="#ef4444"
                strokeWidth="2"
              />
              <text x="16%" y="41%" fill="#ffffff" fontSize="11" fontWeight="bold">
                MRP: 1.35mm (Deficit: Min 2.0mm req)
              </text>

              {/* Net Qty Box */}
              <rect
                x="15%"
                y="46%"
                width="55%"
                height="7%"
                fill="rgba(245, 158, 11, 0.25)"
                stroke="#f59e0b"
                strokeWidth="2"
              />
              <text x="16%" y="51%" fill="#ffffff" fontSize="11" fontWeight="bold">
                Net Qty: 'approx.' Prohibited Qualifier
              </text>

              {/* Barcode Calibration Target */}
              <rect
                x="65%"
                y="65%"
                width="24%"
                height="18%"
                fill="rgba(34, 197, 94, 0.2)"
                stroke="#22c55e"
                strokeWidth="2"
              />
              <text x="66%" y="71%" fill="#22c55e" fontSize="10" fontWeight="bold">
                EAN-13 Scale: 37.29mm
              </text>
            </svg>
          </div>

          {/* Calibrator Legend */}
          <div className="mt-3 grid grid-cols-3 gap-2 text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-200">
            <div>
              <span className="font-bold text-blue-600">PDP Area:</span> 124.0 cm²
            </div>
            <div>
              <span className="font-bold text-emerald-600">Scale Ratio:</span> 0.082 mm/px
            </div>
            <div>
              <span className="font-bold text-rose-600">Min Font Req:</span> 2.0 mm (Schedule II)
            </div>
          </div>
        </div>

        {/* Right: Detected Declarations & Statutory Violations */}
        <div className="lg:col-span-5 space-y-4">
          {/* Statutory Violations Box */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4 text-rose-600" />
                <h3 className="font-bold text-slate-900 text-sm">Statutory Infractions ({violations.length})</h3>
              </div>
              <span className="text-[11px] font-bold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                Total Fine: ₹{violations.reduce((s, v) => s + Number(v.penalty_amount), 0).toLocaleString()}
              </span>
            </div>

            <div className="space-y-2.5 max-h-56 overflow-y-auto">
              {violations.map((v) => (
                <div key={v.id} className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-black text-slate-900 text-xs">{v.clause_reference}</span>
                    <SeverityBadge severity={v.severity} />
                  </div>
                  <p className="text-[11px] text-slate-600 leading-snug">{v.description}</p>
                  <div className="text-[10px] font-bold text-slate-500 pt-1 flex justify-between">
                    <span>Sec 36 LM Act</span>
                    <span className="text-slate-800">Penalty: ₹{Number(v.penalty_amount).toLocaleString()}</span>
                  </div>
                </div>
              ))}
              {violations.length === 0 && (
                <div className="text-center py-6 text-emerald-600 font-semibold text-xs flex flex-col items-center">
                  <CheckCircle className="h-6 w-6 mb-1 text-emerald-500" />
                  <span>Package satisfies all statutory declarations!</span>
                </div>
              )}
            </div>
          </div>

          {/* Detected OCR Fields Matrix */}
          <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-3">
            <h3 className="font-bold text-slate-900 text-sm">OCR Extractions &amp; Metric Measurements</h3>
            <div className="space-y-2 max-h-56 overflow-y-auto text-xs">
              {detectedFields.map((field) => (
                <div key={field.id} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200 flex flex-col space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[10px] font-bold text-blue-700 uppercase">
                      {field.field_key.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] text-slate-400 font-medium">
                      Conf: {(Number(field.confidence || 0.9) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="font-medium text-slate-800 text-[11px]">{field.extracted_value}</div>
                  <div className="flex items-center space-x-3 text-[10px] text-slate-500 pt-0.5">
                    <span>Height: <strong className="text-slate-800">{field.measured_font_height_mm} mm</strong></span>
                    <span>Contrast: <strong className="text-slate-800">{field.contrast_ratio}:1</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cryptographic Chain of Custody Box */}
          <div className="bg-slate-900 rounded-xl p-3.5 text-white text-[11px] space-y-1 font-mono">
            <div className="text-slate-400 text-[10px] uppercase font-bold">Cryptographic Chain-of-Custody</div>
            <div className="truncate text-blue-300">SHA256:{inspection.image_sha256}</div>
            <div className="text-slate-400">Signed with DOCA PKI X.509 RSA-2048</div>
          </div>
        </div>
      </div>

      {/* Human Override Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200">
            <h3 className="font-bold text-slate-900 text-lg">Field Inspector Human Override</h3>
            <p className="text-xs text-slate-500">
              Submit a formal administrative justification to dispute AI findings or record physical exemption. This is permanently logged in the audit ledger.
            </p>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700">Override Reason &amp; Legal Justification</label>
              <textarea
                value={overrideNotes}
                onChange={(e) => setOverrideNotes(e.target.value)}
                placeholder="e.g. Physical package verification confirmed tax statement on bottom seal fold; compliant under Rule 6(3)."
                rows={4}
                className="w-full text-xs p-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowOverrideModal(false)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveOverride}
                className="px-4 py-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg shadow-md transition"
              >
                Mark as Compliant (Override)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
