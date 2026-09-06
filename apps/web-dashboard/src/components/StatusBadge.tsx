import React from 'react';
import { InspectionStatus } from '../types';

export const StatusBadge: React.FC<{ status: InspectionStatus }> = ({ status }) => {
  const styles = {
    PENDING: 'bg-slate-100 text-slate-700 border-slate-300',
    COMPLIANT: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    FLAGGED: 'bg-rose-100 text-rose-800 border-rose-300 animate-pulse',
    NOTICE_ISSUED: 'bg-purple-100 text-purple-800 border-purple-300',
  };

  const labels = {
    PENDING: 'ANALYSIS PENDING',
    COMPLIANT: 'COMPLIANT',
    FLAGGED: 'VIOLATION FLAGGED',
    NOTICE_ISSUED: 'NOTICE ISSUED',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[11px] font-extrabold border uppercase tracking-wider ${styles[status] || styles.PENDING}`}>
      {labels[status] || status}
    </span>
  );
};
