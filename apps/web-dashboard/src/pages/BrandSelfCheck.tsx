import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, AlertTriangle, FileCheck, Shield, ArrowRight, Download } from 'lucide-react';

export const BrandSelfCheck: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = () => {
    if (!file) return;
    setAnalyzing(true);
    // Simulate pre-market statutory audit analysis
    setTimeout(() => {
      setAnalyzing(false);
      setResult({
        score: 92,
        status: 'MOSTLY_COMPLIANT',
        brand: 'Organic Delight Oats',
        pdp_area_cm2: 185.0,
        checks: [
          { rule: 'Rule 6(1)(a)', title: 'Manufacturer Complete Address', status: 'PASS', detail: 'Valid pincode and company details detected.' },
          { rule: 'Rule 6(1)(b)', title: 'Net Quantity SI Units', status: 'PASS', detail: 'Net Qty: 400 g in standard SI units without qualifiers.' },
          { rule: 'Rule 6(1)(c)', title: 'MRP & Tax Phrasing', status: 'WARN', detail: "Phrase 'incl. taxes' found; recommend standard 'incl. of all taxes'." },
          { rule: 'Rule 6(1)(d)', title: 'Month & Year of Manufacture', status: 'PASS', detail: 'Mfg: 08/2026 clearly declared.' },
          { rule: 'Rule 6(1)(e)', title: 'Consumer Helpline & Grievance', status: 'PASS', detail: 'Toll-free 1800 and email verified.' },
          { rule: 'Schedule II', title: 'Minimum Font Height Threshold', status: 'PASS', detail: 'Numerals: 2.3 mm (exceeds 2.0 mm requirement for 185 cm² PDP).' }
        ]
      });
    }, 1800);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-2">
        <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-50 text-emerald-700 font-bold text-xs rounded-full border border-emerald-200">
          <Shield className="h-3.5 w-3.5" />
          <span>DOCA Voluntary Pre-Market Self-Check</span>
        </div>
        <h2 className="text-2xl font-black text-slate-900 tracking-tight">FMCG Brand Packaging Compliance Portal</h2>
        <p className="text-xs text-slate-500 leading-relaxed max-w-2xl">
          Upload pre-print packaging artwork or 3D carton mockups to verify statutory conformity under the Legal Metrology (Packaged Commodities) Rules, 2011 prior to retail distribution.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div className="bg-white rounded-2xl p-8 border-2 border-dashed border-slate-300 hover:border-blue-500 transition text-center space-y-4 shadow-sm">
        <div className="inline-flex p-4 bg-blue-50 text-blue-600 rounded-full">
          <UploadCloud className="h-8 w-8" />
        </div>
        <div>
          <h3 className="font-bold text-slate-900 text-sm">Upload Label Artwork (PDF, PNG, JPG)</h3>
          <p className="text-xs text-slate-500 mt-1">High resolution artwork files up to 50MB</p>
        </div>
        <div>
          <input
            type="file"
            id="artwork-upload"
            onChange={handleUpload}
            className="hidden"
            accept="image/*,.pdf"
          />
          <label
            htmlFor="artwork-upload"
            className="inline-flex items-center space-x-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg cursor-pointer transition"
          >
            <span>{file ? file.name : 'Select File from Computer'}</span>
          </label>
        </div>

        {file && (
          <div className="pt-2">
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-300 text-white text-xs font-bold rounded-xl shadow-md transition"
            >
              {analyzing ? 'Analyzing Statutory Rules...' : 'Run Automated Pre-Market Audit'}
            </button>
          </div>
        )}
      </div>

      {/* Audit Scorecard Results */}
      {result && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-5 animate-in fade-in duration-300">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Pre-Market Audit Scorecard</span>
              <h3 className="text-xl font-black text-slate-900">{result.brand}</h3>
              <p className="text-xs text-slate-500">PDP Area Calculated: {result.pdp_area_cm2} cm²</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-black text-emerald-600">{result.score}/100</div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                Ready for Printing
              </span>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-bold text-xs uppercase tracking-wider text-slate-600">Clause-by-Clause Check</h4>
            {result.checks.map((check: any, idx: number) => (
              <div key={idx} className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-start justify-between gap-4">
                <div className="space-y-0.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-[10px] font-bold text-blue-700">{check.rule}</span>
                    <span className="font-bold text-slate-800 text-xs">{check.title}</span>
                  </div>
                  <p className="text-[11px] text-slate-500">{check.detail}</p>
                </div>
                <div>
                  {check.status === 'PASS' ? (
                    <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>PASS</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center space-x-1 text-[11px] font-bold text-amber-700 bg-amber-100/60 px-2 py-0.5 rounded">
                      <AlertTriangle className="h-3 w-3" />
                      <span>ADVISORY</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => alert("Downloading DOCA Pre-Market Conformity Certificate (PDF)")}
              className="inline-flex items-center space-x-2 text-xs font-bold text-blue-600 hover:text-blue-800"
            >
              <Download className="h-4 w-4" />
              <span>Download Pre-Market Advisory Certificate (PDF)</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
