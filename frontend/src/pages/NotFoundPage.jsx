import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="page-shell">
      <div className="empty-subtle py-8">
        <h1 className="text-2xl font-bold mb-2">404</h1>
        <p className="text-secondary mb-4">The page you are looking for does not exist.</p>
        <Link to="/" className="btn btn-secondary">
          Return to Dashboard
        </Link>
      </div>
    </div>
  );
}
