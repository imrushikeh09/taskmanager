import React, { Component, StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Task Manager UI Error Boundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "100vh",
            background: "#0D0E12",
            color: "#F0F2F5",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "2rem",
            fontFamily: "Inter, sans-serif",
          }}
        >
          <div
            style={{
              maxWidth: "460px",
              width: "100%",
              background: "#15161C",
              border: "1px solid rgba(255, 255, 255, 0.12)",
              borderRadius: "8px",
              padding: "1.75rem",
              boxShadow: "0 16px 36px rgba(0, 0, 0, 0.6)",
            }}
          >
            <h2 style={{ fontSize: "16px", marginBottom: "0.5rem", color: "#E5484D" }}>
              Workspace Runtime Recovery
            </h2>
            <p style={{ fontSize: "12px", color: "#9DA1AA", marginBottom: "1rem" }}>
              A client runtime exception occurred. Click below to reload your workspace.
            </p>
            <pre
              style={{
                fontSize: "11px",
                background: "#111217",
                padding: "0.75rem",
                borderRadius: "4px",
                border: "1px solid rgba(255, 255, 255, 0.07)",
                color: "#F87171",
                marginBottom: "1.25rem",
                overflowX: "auto",
              }}
            >
              {this.state.error?.message || "Unknown rendering exception"}
            </pre>
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
              <button
                className="btn btn-secondary"
                onClick={() => {
                  localStorage.clear();
                  window.location.reload();
                }}
              >
                Clear Cache & Reset
              </button>
              <button
                className="btn btn-primary"
                onClick={() => window.location.reload()}
              >
                Reload Workspace
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </StrictMode>
);
