import React from "react";
import { CheckCircle2, Clock, AlertTriangle, Layers } from "lucide-react";

export default function ProjectStats({ tasks = [] }) {
  const total = tasks.length;
  const completed = tasks.filter((t) => t.status === "COMPLETED").length;
  const inProgress = tasks.filter((t) => t.status === "IN_PROGRESS").length;
  const blocked = tasks.filter((t) => t.status === "BLOCKED").length;
  const rate = total > 0 ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="metrics-strip">
      <div className="metric-pill">
        <Layers size={13} style={{ color: "var(--brand-primary)" }} />
        <span>Total Issues:</span>
        <span className="metric-value">{total}</span>
      </div>

      <div className="metric-pill">
        <Clock size={13} style={{ color: "var(--status-progress)" }} />
        <span>In Progress:</span>
        <span className="metric-value">{inProgress}</span>
      </div>

      <div className="metric-pill">
        <AlertTriangle size={13} style={{ color: "var(--status-blocked)" }} />
        <span>Blocked:</span>
        <span className="metric-value">{blocked}</span>
      </div>

      <div className="metric-pill">
        <CheckCircle2 size={13} style={{ color: "var(--status-done)" }} />
        <span>Completed:</span>
        <span className="metric-value">
          {completed} ({rate}%)
        </span>
      </div>

      {total > 0 && (
        <div
          style={{
            flex: 1,
            minWidth: "100px",
            maxWidth: "180px",
            height: "4px",
            background: "rgba(255, 255, 255, 0.08)",
            borderRadius: "var(--radius-full)",
            overflow: "hidden",
            marginLeft: "auto",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${rate}%`,
              background: "var(--status-done)",
              transition: "width 0.3s ease",
            }}
          />
        </div>
      )}
    </div>
  );
}
