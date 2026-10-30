import React from 'react';

export default function ProjectStatsCard({ stats, performance }) {
  if (!stats) return null;

  const total = stats.total_tasks || 0;
  const byStatus = stats.by_status || {};
  const byPriority = stats.by_priority || {};

  const todoCount = byStatus.TODO || 0;
  const inProgressCount = byStatus.IN_PROGRESS || 0;
  const blockedCount = byStatus.BLOCKED || 0;
  const completedCount = byStatus.COMPLETED || 0;

  const completionPct = total > 0 ? Math.round((completedCount / total) * 100) : 0;

  return (
    <div className="card project-stats-card">
      {/* Metric counters */}
      <div className="metrics-strip">
        <div className="metric-cell">
          <span className="metric-label">Total</span>
          <span className="metric-num">{total}</span>
        </div>
        <div className="metric-cell">
          <span className="metric-label">In Progress</span>
          <span className="metric-num text-info">{inProgressCount}</span>
        </div>
        <div className="metric-cell">
          <span className="metric-label">Blocked</span>
          <span className="metric-num text-danger">{blockedCount}</span>
        </div>
        <div className="metric-cell">
          <span className="metric-label">Completed</span>
          <span className="metric-num text-success">{completedCount}</span>
        </div>
        {performance?.metrics?.overdue_tasks !== undefined && (
          <div className="metric-cell">
            <span className="metric-label">Overdue</span>
            <span className="metric-num text-danger">{performance.metrics.overdue_tasks}</span>
          </div>
        )}
      </div>

      {/* Progress */}
      <div className="stats-progress-wrap">
        <div className="progress-labels">
          <span className="font-medium text-secondary">Progress</span>
          <span className="caption font-medium">{completionPct}% completed</span>
        </div>
        <div className="progress-track">
          <div
            className="progress-segment seg-completed"
            style={{ width: `${total > 0 ? (completedCount / total) * 100 : 0}%` }}
          />
          <div
            className="progress-segment seg-in-progress"
            style={{ width: `${total > 0 ? (inProgressCount / total) * 100 : 0}%` }}
          />
          <div
            className="progress-segment seg-blocked"
            style={{ width: `${total > 0 ? (blockedCount / total) * 100 : 0}%` }}
          />
          <div
            className="progress-segment seg-todo"
            style={{ width: `${total > 0 ? (todoCount / total) * 100 : 0}%` }}
          />
        </div>
        <div className="progress-legend">
          <span className="legend-item"><span className="legend-dot dot-completed"></span> Completed ({completedCount})</span>
          <span className="legend-item"><span className="legend-dot dot-in-progress"></span> In Progress ({inProgressCount})</span>
          <span className="legend-item"><span className="legend-dot dot-blocked"></span> Blocked ({blockedCount})</span>
          <span className="legend-item"><span className="legend-dot dot-todo"></span> To Do ({todoCount})</span>
        </div>
      </div>

      {/* Urgency breakdown */}
      <div className="priority-strip">
        <span className="caption font-medium text-muted">Priority:</span>
        <div className="priority-pills">
          <span className="pill pill-urgent">Urgent: {byPriority.URGENT || 0}</span>
          <span className="pill pill-high">High: {byPriority.HIGH || 0}</span>
          <span className="pill pill-medium">Medium: {byPriority.MEDIUM || 0}</span>
          <span className="pill pill-low">Low: {byPriority.LOW || 0}</span>
        </div>
      </div>
    </div>
  );
}
