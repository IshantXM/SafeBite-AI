import React from 'react';
import { ViolationSeverity } from '../types';

export const SeverityBadge: React.FC<{ severity: ViolationSeverity }> = ({ severity }) => {
  const styles = {
    CRITICAL: 'bg-rose-100 text-rose-800 border-rose-200',
    HIGH: 'bg-amber-100 text-amber-800 border-amber-200',
    MEDIUM: 'bg-blue-100 text-blue-800 border-blue-200',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold border ${styles[severity] || styles.HIGH}`}>
      {severity}
    </span>
  );
};
