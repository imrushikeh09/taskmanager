import React from 'react';

export default function EmptyState({ title = 'No records found', description, action }) {
  return (
    <div className="card empty-state">
      <h3 className="empty-title">{title}</h3>
      {description && <p className="empty-desc text-secondary">{description}</p>}
      {action && <div className="empty-action">{action}</div>}
    </div>
  );
}
