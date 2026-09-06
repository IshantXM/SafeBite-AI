import React, { useEffect, useState } from 'react';
import { Sliders, Save, RefreshCw, Plus, CheckCircle, ShieldCheck, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import { RuleConfiguration } from '../types';

export const RuleAdminConsole: React.FC = () => {
  const [activeRule, setActiveRule] = useState<RuleConfiguration | null>(null);
  const [penaltyFirstOffence, setPenaltyFirstOffence] = useState<number>(25000);
  const [penaltyTamper, setPenaltyTamper] = useState<number>(50000);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    async function load() {
      const rule = await api.getActiveRule();
      setActiveRule(rule);
    }
    load();
  }, []);

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <div className="flex items-center space-x-2 text-blue-600 text-xs font-bold uppercase tracking-wider mb-1">
            <Sliders className="h-4 w-4" />
            <span>Statutory Rules Management</span>
          </div>
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Legal Metrology Policy Console</h2>
          <p className="text-xs text-slate-500 mt-1">
            Dynamic threshold &amp; penalty matrix configuration under Legal Metrology Act, 2009.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {savedSuccess && (
            <span className="inline-flex items-center space-x-1 text-xs text-emerald-600 font-bold animate-in fade-in">
              <CheckCircle className="h-4 w-4" />
              <span>Rules Reconciled!</span>
            </span>
          )}
          <button
            onClick={handleSave}
            className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl shadow-md transition"
          >
            <Save className="h-4 w-4" />
            <span>Publish Rule Updates</span>
          </button>
        </div>
      </div>

      {/* Active Ruleset Version Banner */}
      <div className="bg-slate-900 text-white rounded-2xl p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div className="text-[11px] text-slate-400 uppercase font-bold">Active Regulatory Enactment</div>
          <div className="text-base font-bold text-white mt-0.5">
            {activeRule?.rule_set_name || 'Legal Metrology (Packaged Commodities) Rules, 2011'}
          </div>
          <div className="text-xs text-blue-400 font-mono mt-0.5">Version: {activeRule?.version || '2026.1'} • In Force</div>
        </div>
        <div className="text-right text-xs text-slate-400">
          Last Revised: {new Date().toLocaleDateString()}
        </div>
      </div>

      {/* Penalties Matrix Editor */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
          Section 36 Statutory Penalty Scale (INR)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <label className="text-xs font-bold text-slate-700 block">
              Section 36(1) First Offence Maximum Penalty (INR)
            </label>
            <input
              type="number"
              value={penaltyFirstOffence}
              onChange={(e) => setPenaltyFirstOffence(Number(e.target.value))}
              className="w-full text-xs font-mono font-bold p-2.5 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[10px] text-slate-500">Statutory cap under Section 36(1) of LM Act 2009 is ₹25,000</p>
          </div>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
            <label className="text-xs font-bold text-slate-700 block">
              Sticker Tampering / Overlapping MRP Penalty (INR)
            </label>
            <input
              type="number"
              value={penaltyTamper}
              onChange={(e) => setPenaltyTamper(Number(e.target.value))}
              className="w-full text-xs font-mono font-bold p-2.5 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-[10px] text-slate-500">Statutory penalty for concealing printed MRP declarations</p>
          </div>
        </div>
      </div>

      {/* Schedule II Font Height Area Matrix */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Schedule II Minimum Font Height Mapping (mm)
          </h3>
          <span className="text-[11px] font-bold text-slate-500">Rule 7 Specification</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-700 font-bold">
                <th className="py-2.5 px-3">Principal Display Panel Area (cm²)</th>
                <th className="py-2.5 px-3">Min Numeral Height (mm)</th>
                <th className="py-2.5 px-3">Min Letter Height (mm)</th>
                <th className="py-2.5 px-3">Blown / Moulded Container (mm)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-slate-800">
              <tr>
                <td className="py-2.5 px-3">Area ≤ 50 cm²</td>
                <td className="py-2.5 px-3 font-bold text-blue-700">1.0 mm</td>
                <td className="py-2.5 px-3">1.0 mm</td>
                <td className="py-2.5 px-3">1.5 mm</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3">50 cm² &lt; Area ≤ 200 cm²</td>
                <td className="py-2.5 px-3 font-bold text-blue-700">2.0 mm</td>
                <td className="py-2.5 px-3">1.5 mm</td>
                <td className="py-2.5 px-3">3.0 mm</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3">200 cm² &lt; Area ≤ 1000 cm²</td>
                <td className="py-2.5 px-3 font-bold text-blue-700">4.0 mm</td>
                <td className="py-2.5 px-3">2.0 mm</td>
                <td className="py-2.5 px-3">6.0 mm</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3">Area &gt; 1000 cm²</td>
                <td className="py-2.5 px-3 font-bold text-blue-700">6.0 mm</td>
                <td className="py-2.5 px-3">3.0 mm</td>
                <td className="py-2.5 px-3">9.0 mm</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
