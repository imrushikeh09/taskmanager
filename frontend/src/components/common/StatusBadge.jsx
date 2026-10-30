import React from 'react';

const STATUS_CONFIG = {
  TODO: {
    label: 'To Do',
    colorClass: 'status-todo',
  },
  IN_PROGRESS: {
    label: 'In Progress',
    colorClass: 'status-in-progress',
  },
  BLOCKED: {
    label: 'Blocked',
    colorClass: 'status-blocked',
  },
  COMPLETED: {
    label: 'Completed',
    colorClass: 'status-completed',
  },
};

export default function StatusBadge({ status, className = '' }) {
  const config = STATUS_CONFIG[status] || {
    label: status ? status.replace('_', ' ') : 'Unknown',
    colorClass: 'status-default',
  };

  return (
    <span className={`status-badge ${config.colorClass} ${className}`}>
      <span className="status-dot"></span>
      <span className="status-text">{config.label}</span>
    </span>
  );
}
