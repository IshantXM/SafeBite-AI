import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  iconColor?: string;
  trend?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  iconColor = 'text-blue-500',
  trend
}) => {
  return (
    <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</p>
          <h3 className="text-2xl font-black text-slate-900 mt-1">{value}</h3>
        </div>
        <div className={`p-3 rounded-xl bg-slate-50 border border-slate-100 ${iconColor}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
      {(subtext || trend) && (
        <div className="mt-3 flex items-center text-xs space-x-2">
          {trend && <span className="font-semibold text-emerald-600">{trend}</span>}
          {subtext && <span className="text-slate-400">{subtext}</span>}
        </div>
      )}
    </div>
  );
};
