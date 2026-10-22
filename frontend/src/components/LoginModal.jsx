import React, { useState } from "react";
import { CheckSquare, AlertCircle, ArrowRight } from "lucide-react";
import { login } from "../services/api";

export default function LoginModal({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await login(username, password);
      onLoginSuccess();
    } catch (err) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fillQuickCredentials = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Brand */}
        <div className="auth-brand">
          <div className="auth-brand-logo">
            <CheckSquare size={16} strokeWidth={2.5} />
          </div>
          <span style={{ fontSize: "14px", fontWeight: 700, color: "var(--text-primary)" }}>
            TaskManager
          </span>
        </div>

        <h1 className="auth-title">Sign in to workspace</h1>
        <p className="auth-subtitle">Enter your enterprise credentials</p>

        {error && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              background: "rgba(229, 72, 77, 0.1)",
              border: "1px solid rgba(229, 72, 77, 0.3)",
              color: "#F87171",
              padding: "0.5rem 0.75rem",
              borderRadius: "var(--radius-sm)",
              marginBottom: "1rem",
              fontSize: "12px",
            }}
          >
            <AlertCircle size={14} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. admin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
            />
          </div>

          <div className="form-group" style={{ marginBottom: "1.25rem" }}>
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: "100%", padding: "0.5rem" }}
            disabled={loading}
          >
            <span>{loading ? "Signing in..." : "Continue"}</span>
            {!loading && <ArrowRight size={14} />}
          </button>
        </form>

        <div
          style={{
            marginTop: "1.5rem",
            paddingTop: "1rem",
            borderTop: "1px solid var(--border-subtle)",
            textAlign: "center",
            fontSize: "11px",
            color: "var(--text-muted)",
          }}
        >
          <span>Demo evaluation: </span>
          <button
            type="button"
            onClick={() => fillQuickCredentials("admin", "admin123")}
            style={{
              background: "none",
              border: "none",
              color: "var(--brand-primary)",
              cursor: "pointer",
              fontWeight: 600,
              textDecoration: "underline",
              fontSize: "11px",
            }}
          >
            Use admin / admin123
          </button>
        </div>
      </div>
    </div>
  );
}
