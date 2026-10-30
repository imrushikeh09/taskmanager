import React from 'react';

export default function LoadingSpinner({ text = 'Loading...', size = 'medium' }) {
  return (
    <div className={`loading-wrapper loading-${size}`}>
      <div className="spinner-ring"></div>
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
}

