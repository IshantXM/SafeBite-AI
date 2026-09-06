import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Camera, Kanban, ScanEye, CheckCircle2, Sliders, Scale } from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: '/scanner', label: 'Live Camera Scanner', icon: Camera, highlight: true },
    { to: '/', label: 'Command Center', icon: LayoutDashboard },
    { to: '/cases', label: 'Case Kanban', icon: Kanban },
    { to: '/inspector', label: 'Evidence Inspector', icon: ScanEye },
    { to: '/self-check', label: 'Brand Self-Check', icon: CheckCircle2 },
    { to: '/rules-admin', label: 'Statutory Rules', icon: Sliders },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
          Enforcement Modules
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25 font-semibold'
                    : item.highlight
                    ? 'text-sky-300 bg-blue-950/40 hover:bg-blue-900/60 border border-blue-800/40'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className={`h-4 w-4 ${item.highlight ? 'text-sky-400' : ''}`} />
              <span>{item.label}</span>
              {item.highlight && (
                <span className="ml-auto text-[9px] bg-sky-500/20 text-sky-300 font-extrabold px-1.5 py-0.5 rounded border border-sky-400/30">
                  LIVE
                </span>
              )}
            </NavLink>
          );
        })}
      </div>

      <div className="bg-slate-800/60 rounded-xl p-3.5 border border-slate-700/60 space-y-2">
        <div className="flex items-center space-x-2 text-blue-400">
          <Scale className="h-4 w-4" />
          <span className="text-xs font-bold uppercase tracking-wider">Legal Framework</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-snug">
          Enforcing LM Act 2009 &amp; Packaged Commodities Rules 2011 (as amended 2021).
        </p>
        <div className="text-[10px] text-slate-500 pt-1 border-t border-slate-700/50">
          Version 2026.1 • Official DOCA System
        </div>
      </div>
    </aside>
  );
};
