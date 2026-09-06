import React, { useEffect, useState } from 'react';
import { ShieldAlert, AlertTriangle, CheckCircle2, TrendingUp, IndianRupee, Layers, Eye } from 'lucide-react';
import { Link } from 'react-router-dom';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { AnalyticsSummary, GeoJSONFeatureCollection, RepeatOffender, Inspection } from '../types';

export const CommandCenter: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [heatmaps, setHeatmaps] = useState<GeoJSONFeatureCollection | null>(null);
  const [offenders, setOffenders] = useState<RepeatOffender[]>([]);
  const [recentInspections, setRecentInspections] = useState<Inspection[]>([]);
  const [selectedState, setSelectedState] = useState<string>('All States');

  useEffect(() => {
    async function loadData() {
      const [sumData, heatData, offData, inspData] = await Promise.all([
        api.getSummary(),
        api.getHeatmaps(),
        api.getRepeatOffenders(),
        api.getInspections()
      ]);
      setSummary(sumData);
      setHeatmaps(heatData);
      setOffenders(offData);
      setRecentInspections(inspData);
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-slate-900 to-indigo-950 rounded-2xl p-6 text-white shadow-xl relative overflow-hidden border border-blue-800/40">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-blue-400 text-xs font-bold uppercase tracking-wider mb-1">
              <span>National Operations Hub</span>
              <span>•</span>
              <span>Legal Metrology Act, 2009 Enforcement</span>
            </div>
            <h2 className="text-2xl font-black tracking-tight text-white">Central Compliance Command Center</h2>
            <p className="text-sm text-slate-300 max-w-2xl mt-1">
              Real-time surveillance monitoring packaged commodities across retail and manufacturing touchpoints in India.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Link
              to="/cases"
              className="bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs px-4 py-2.5 rounded-lg shadow-lg shadow-blue-600/30 transition flex items-center space-x-1.5"
            >
              <ShieldAlert className="h-4 w-4" />
              <span>Review 42 Pending</span>
            </Link>
            <Link
              to="/inspector"
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs px-4 py-2.5 rounded-lg border border-slate-700 transition"
            >
              Visual Evidence Inspector
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Inspected Packages"
          value={summary?.total_inspections.toLocaleString() || '1,428'}
          subtext="Across 28 States & UTs"
          icon={Layers}
          iconColor="text-blue-600"
          trend="+14% this month"
        />
        <StatCard
          title="Flagged Non-Compliant"
          value={summary?.flagged_cases.toLocaleString() || '184'}
          subtext="Under Rule 6 & Schedule II"
          icon={AlertTriangle}
          iconColor="text-rose-600"
          trend="20.2% Violation Rate"
        />
        <StatCard
          title="Show Cause Notices Issued"
          value={summary?.notices_issued.toLocaleString() || '96'}
          subtext="PKI Digitally Signed"
          icon={ShieldAlert}
          iconColor="text-purple-600"
        />
        <StatCard
          title="Penalties Assessed"
          value={`₹${((summary?.total_penalties_assessed_inr || 4750000) / 100000).toFixed(2)} Lakh`}
          subtext="Under Section 36 LM Act"
          icon={IndianRupee}
          iconColor="text-emerald-600"
        />
      </div>

      {/* Main Map & Repeat Offenders Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: GIS Map View */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-900 text-base">Regional Violation Density &amp; Seizure Map</h3>
              <p className="text-xs text-slate-500">PostGIS spatial clusters of field enforcement activity</p>
            </div>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="text-xs font-semibold bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option>All States</option>
              <option>National Capital Region (Delhi)</option>
              <option>Maharashtra</option>
              <option>Karnataka</option>
              <option>West Bengal</option>
              <option>Tamil Nadu</option>
            </select>
          </div>

          {/* Interactive Geographic Map Container */}
          <div className="w-full h-80 bg-slate-900 rounded-xl overflow-hidden relative border border-slate-800 flex items-center justify-center">
            {/* Visual GIS Grid Representation */}
            <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]"></div>
            
            <div className="relative z-10 text-center p-6 max-w-md">
              <div className="inline-flex p-3 bg-blue-600/20 text-blue-400 rounded-full border border-blue-500/30 mb-3 animate-pulse">
                <Layers className="h-6 w-6" />
              </div>
              <h4 className="text-white font-bold text-sm">PostGIS Spatial Cluster Map Active</h4>
              <p className="text-xs text-slate-400 mt-1">
                Displaying 6 active enforcement zones with high defect concentrations in Delhi NCR, Mumbai MMR, and Bengaluru.
              </p>
            </div>

            {/* Hotspot Markers */}
            <div className="absolute top-1/4 left-1/2 -translate-x-12 p-2 bg-rose-500/90 text-white text-[10px] font-bold rounded-lg shadow-lg border border-rose-300 flex items-center space-x-1">
              <span className="h-2 w-2 rounded-full bg-white animate-ping"></span>
              <span>Delhi NCR (48 Flagged)</span>
            </div>

            <div className="absolute top-1/2 left-1/3 p-2 bg-amber-500/90 text-white text-[10px] font-bold rounded-lg shadow-lg border border-amber-300 flex items-center space-x-1">
              <span>Mumbai MMR (32 Flagged)</span>
            </div>

            <div className="absolute bottom-1/4 left-2/5 p-2 bg-purple-500/90 text-white text-[10px] font-bold rounded-lg shadow-lg border border-purple-300 flex items-center space-x-1">
              <span>Bengaluru (21 Flagged)</span>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-3">
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-rose-500"></span>
                <span>Critical Violation</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
                <span>High Violation</span>
              </span>
              <span className="flex items-center space-x-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                <span>Compliant</span>
              </span>
            </div>
            <span>Updated live via Field App sync</span>
          </div>
        </div>

        {/* Right: Repeat Non-Compliant Brands */}
        <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-900 text-base">Repeat Offender Watchlist</h3>
              <span className="text-[10px] bg-rose-50 text-rose-700 font-bold px-2 py-0.5 rounded border border-rose-200">
                Sec 36(1)
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-4">Brands with multiple verified statutory non-compliances</p>

            <div className="space-y-3">
              {offenders.map((brand, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 hover:border-slate-300 transition">
                  <div className="flex items-center justify-between">
                    <div className="font-bold text-xs text-slate-800">{brand.brand_name}</div>
                    <div className="text-[11px] font-black text-rose-600">{brand.violation_count} Violations</div>
                  </div>
                  <div className="flex items-center justify-between mt-1 text-[11px] text-slate-500">
                    <span>{brand.category}</span>
                    <span className="font-semibold text-slate-700">₹{(brand.total_penalties_inr / 1000).toFixed(0)}k fine assessed</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100">
            <Link
              to="/cases"
              className="text-xs text-blue-600 hover:text-blue-800 font-semibold flex items-center justify-center space-x-1"
            >
              <span>View all escalated corporate cases →</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Field Inspections Feed */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Recent Field Inspections</h3>
            <p className="text-xs text-slate-500">Real-time synchronized surveillance stream</p>
          </div>
          <Link
            to="/cases"
            className="text-xs font-semibold text-blue-600 hover:text-blue-800"
          >
            View All Cases
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-bold text-[10px] tracking-wider">
                <th className="py-3 px-4">Inspection ID</th>
                <th className="py-3 px-4">Brand / Manufacturer</th>
                <th className="py-3 px-4">Barcode</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Violations</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {recentInspections.map((insp) => (
                <tr key={insp.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                    {insp.id.substring(0, 8)}...
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-900">{insp.brand_name || 'N/A'}</td>
                  <td className="py-3 px-4 font-mono text-slate-600">{insp.barcode || 'N/A'}</td>
                  <td className="py-3 px-4 text-slate-600">{insp.category || 'Commodity'}</td>
                  <td className="py-3 px-4">
                    <StatusBadge status={insp.status} />
                  </td>
                  <td className="py-3 px-4 font-bold text-rose-600">
                    {insp.violations?.length || 0} issues
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      to={`/inspector?id=${insp.id}`}
                      className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 font-bold"
                    >
                      <Eye className="h-3.5 w-3.5" />
                      <span>Inspect</span>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
