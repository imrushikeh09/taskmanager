import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayersIcon } from '../components/common/Icons';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleLogin = async (userToSubmit, passToSubmit) => {
    setError('');
    setIsSubmitting(true);
    try {
      await login(userToSubmit, passToSubmit);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Invalid username or password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError('Please provide both username and password.');
      return;
    }
    handleLogin(username.trim(), password);
  };

  const handleQuickLogin = (userVal, passVal) => {
    setUsername(userVal);
    setPassword(passVal);
    handleLogin(userVal, passVal);
  };

  return (
    <div className="login-shell">
      <div className="card login-card">
        <div className="login-header">
          <div className="brand-mark mb-3">
            <LayersIcon size={20} />
          </div>
          <h2 className="login-title">Sign in to TaskManager</h2>
          <p className="caption text-muted">Enter your credentials to access your workspace</p>
        </div>

        {error && <div className="alert alert-danger">{error}</div>}

        <form onSubmit={handleSubmit} className="form">
          <div className="form-field">
            <label htmlFor="login-username" className="label">
              Username
            </label>
            <input
              id="login-username"
              type="text"
              className="input"
              placeholder="e.g. admin or sarah.chen"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
            />
          </div>

          <div className="form-field">
            <label htmlFor="login-password" className="label">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              className="input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={isSubmitting}>
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Accounts */}
        <div className="demo-accounts-box">
          <span className="caption font-medium text-muted uppercase">Quick test credentials</span>
          <div className="demo-list">
            <button
              type="button"
              className="demo-pill"
              onClick={() => handleQuickLogin('admin', 'admin123')}
              disabled={isSubmitting}
            >
              <span className="font-medium">Admin</span>
              <span className="caption text-muted font-mono">admin / admin123</span>
            </button>
            <button
              type="button"
              className="demo-pill"
              onClick={() => handleQuickLogin('sarah.chen', 'user123')}
              disabled={isSubmitting}
            >
              <span className="font-medium">Contributor</span>
              <span className="caption text-muted font-mono">sarah.chen / user123</span>
            </button>
            <button
              type="button"
              className="demo-pill"
              onClick={() => handleQuickLogin('priya.qa', 'user123')}
              disabled={isSubmitting}
            >
              <span className="font-medium">Viewer (Read-Only)</span>
              <span className="caption text-muted font-mono">priya.qa / user123</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
