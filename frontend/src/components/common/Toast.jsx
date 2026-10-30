import React from 'react';

export default function Toast({ message, type = 'info', onClose }) {
  if (!message) return null;

  return (
    <div className={`toast-alert toast-${type}`}>
      <span className="toast-icon">
        {type === 'success' && '✓'}
        {type === 'error' && '⚠'}
        {type === 'info' && 'ℹ'}
      </span>
      <span className="toast-message">{message}</span>
      {onClose && (
        <button className="toast-close" onClick={onClose}>
          ✕
        </button>
      )}
    </div>
  );
}

