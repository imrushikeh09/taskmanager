import React from 'react';

const PRIORITY_CONFIG = {
  LOW: {
    label: 'Low',
    className: 'priority-low',
  },
  MEDIUM: {
    label: 'Medium',
    className: 'priority-medium',
  },
  HIGH: {
    label: 'High',
    className: 'priority-high',
  },
  URGENT: {
    label: 'Urgent',
    className: 'priority-urgent',
  },
};

export default function PriorityBadge({ priority, className = '' }) {
  const config = PRIORITY_CONFIG[priority] || {
    label: priority || 'Medium',
    className: 'priority-medium',
  };

  return (
    <span className={`priority-badge ${config.className} ${className}`}>
      {config.label}
    </span>
  );
}
