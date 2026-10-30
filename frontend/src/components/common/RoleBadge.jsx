import React from 'react';

const ROLE_CONFIG = {
  ADMIN: {
    label: 'Admin',
    colorClass: 'role-admin',
  },
  CONTRIBUTOR: {
    label: 'Contributor',
    colorClass: 'role-contributor',
  },
  VIEWER: {
    label: 'Viewer',
    colorClass: 'role-viewer',
  },
};

export default function RoleBadge({ role, className = '' }) {
  const config = ROLE_CONFIG[role] || {
    label: role || 'Member',
    colorClass: 'role-member',
  };

  return (
    <span className={`role-badge ${config.colorClass} ${className}`}>
      {config.label}
    </span>
  );
}

