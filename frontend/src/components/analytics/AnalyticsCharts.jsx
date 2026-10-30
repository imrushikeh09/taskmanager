import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import StatusBadge from '../common/StatusBadge';
import PriorityBadge from '../common/PriorityBadge';
import { ArrowRightIcon } from '../common/Icons';

export default function AnalyticsCharts({
  tasks = [],
  projects = [],
  onStatusChange,
  canEdit = false,
}) {
  const [selectedStatusFilter, setSelectedStatusFilter] = useState('ALL');

  const totalTasks = tasks.length;

  // Status Counts
  const todoCount = tasks.filter((t) => t.status === 'TODO').length;
  const inProgressCount = tasks.filter((t) => t.status === 'IN_PROGRESS').length;
  const blockedCount = tasks.filter((t) => t.status === 'BLOCKED').length;
  const completedCount = tasks.filter((t) => t.status === 'COMPLETED').length;

  const completionRate = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  // Status Segments for Donut
  const statusSegments = [
    { id: 'COMPLETED', label: 'Completed', count: completedCount, colorVar: 'var(--status-completed)', colorDot: 'dot-completed' },
    { id: 'IN_PROGRESS', label: 'In Progress', count: inProgressCount, colorVar: 'var(--status-in-progress)', colorDot: 'dot-in-progress' },
    { id: 'BLOCKED', label: 'Blocked', count: blockedCount, colorVar: 'var(--status-blocked)', colorDot: 'dot-blocked' },
    { id: 'TODO', label: 'To Do', count: todoCount, colorVar: 'var(--status-todo)', colorDot: 'dot-todo' },
  ];

  // Priority Counts
  const urgentCount = tasks.filter((t) => t.priority === 'URGENT').length;
  const highCount = tasks.filter((t) => t.priority === 'HIGH').length;
  const mediumCount = tasks.filter((t) => t.priority === 'MEDIUM').length;
  const lowCount = tasks.filter((t) => t.priority === 'LOW').length;

  const prioritySegments = [
    { label: 'Urgent', count: urgentCount, color: 'var(--priority-urgent)', pct: totalTasks > 0 ? (urgentCount / totalTasks) * 100 : 0 },
    { label: 'High', count: highCount, color: 'var(--priority-high)', pct: totalTasks > 0 ? (highCount / totalTasks) * 100 : 0 },
    { label: 'Medium', count: mediumCount, color: 'var(--priority-medium)', pct: totalTasks > 0 ? (mediumCount / totalTasks) * 100 : 0 },
    { label: 'Low', count: lowCount, color: 'var(--priority-low)', pct: totalTasks > 0 ? (lowCount / totalTasks) * 100 : 0 },
  ];

  // SVG Donut calculation
  const radius = 46;
  const circumference = 2 * Math.PI * radius; // ~289.026
  let accumulatedLength = 0;

  const donutArcs = statusSegments.map((segment) => {
    const fraction = totalTasks > 0 ? segment.count / totalTasks : 0;
    const strokeLength = fraction * circumference;
    const dashOffset = -accumulatedLength;
    accumulatedLength += strokeLength;
    return {
      ...segment,
      fraction,
      strokeLength,
      dashOffset,
      percent: Math.round(fraction * 100),
    };
  });

  // Filtered task drill-down
  const filteredTasks = tasks.filter((t) => {
    if (selectedStatusFilter === 'ALL') return true;
    return t.status === selectedStatusFilter;
  });

  return (
    <div className="analytics-view">
      {/* Top Visual Graph Grid */}
      <div className="analytics-graphs-grid">
        {/* Status Distribution Donut Chart */}
        <div className="card chart-card">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Status Distribution</h2>
              <p className="caption text-secondary">Breakdown across task lifecycle stages</p>
            </div>
            {selectedStatusFilter !== 'ALL' && (
              <button
                className="btn btn-ghost btn-xs"
                onClick={() => setSelectedStatusFilter('ALL')}
              >
                Reset Filter
              </button>
            )}
          </div>

          <div className="donut-chart-container">
            <div className="donut-svg-wrap">
              <svg viewBox="0 0 120 120" className="donut-svg">
                {/* Background Track */}
                <circle
                  cx="60"
                  cy="60"
                  r={radius}
                  fill="none"
                  stroke="var(--chart-track)"
                  strokeWidth="12"
                />
                {/* Interactive Donut Arcs */}
                {donutArcs.map((arc) => {
                  if (arc.strokeLength <= 0) return null;
                  const isSelected = selectedStatusFilter === arc.id;
                  return (
                    <circle
                      key={arc.id}
                      cx="60"
                      cy="60"
                      r={radius}
                      fill="none"
                      stroke={arc.colorVar}
                      strokeWidth={isSelected ? '14' : '11'}
                      strokeDasharray={`${arc.strokeLength} ${circumference - arc.strokeLength}`}
                      strokeDashoffset={arc.dashOffset}
                      className={`donut-arc ${isSelected ? 'is-active' : ''}`}
                      onClick={() =>
                        setSelectedStatusFilter((prev) => (prev === arc.id ? 'ALL' : arc.id))
                      }
                      transform="rotate(-90 60 60)"
                    />
                  );
                })}
              </svg>

              {/* Center Metrics in Donut */}
              <div className="donut-center-metric">
                <span className="donut-rate">{completionRate}%</span>
                <span className="donut-label">Done</span>
              </div>
            </div>

            {/* Interactive Legend */}
            <div className="chart-legend">
              {donutArcs.map((item) => {
                const isSelected = selectedStatusFilter === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    className={`legend-row ${isSelected ? 'is-selected' : ''}`}
                    onClick={() =>
                      setSelectedStatusFilter((prev) => (prev === item.id ? 'ALL' : item.id))
                    }
                  >
                    <div className="legend-label-col">
                      <span className={`status-dot ${item.colorDot}`}></span>
                      <span className="legend-title">{item.label}</span>
                    </div>
                    <div className="legend-stats">
                      <span className="legend-count">{item.count}</span>
                      <span className="legend-percent text-muted">
                        ({item.percent}%)
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Priority & Workload Breakdown */}
        <div className="card chart-card">
          <div className="chart-header">
            <div>
              <h2 className="chart-title">Priority & Urgency</h2>
              <p className="caption text-secondary">Task workload by priority level</p>
            </div>
          </div>

          <div className="priority-meter-container">
            {/* Segmented Stacked Bar */}
            <div className="priority-segmented-bar">
              {prioritySegments.map(
                (seg) =>
                  seg.pct > 0 && (
                    <div
                      key={seg.label}
                      className="priority-bar-seg"
                      style={{ width: `${seg.pct}%`, backgroundColor: seg.color }}
                      title={`${seg.label}: ${seg.count} tasks (${Math.round(seg.pct)}%)`}
                    />
                  )
              )}
            </div>

            {/* Priority Legend Grid */}
            <div className="priority-grid-legend">
              {prioritySegments.map((seg) => (
                <div key={seg.label} className="priority-metric-cell">
                  <div className="priority-metric-head">
                    <span
                      className="priority-indicator-dot"
                      style={{ backgroundColor: seg.color }}
                    ></span>
                    <span className="caption font-medium">{seg.label}</span>
                  </div>
                  <div className="priority-metric-val">
                    <span className="metric-num-lg">{seg.count}</span>
                    <span className="caption text-muted">({Math.round(seg.pct)}%)</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Project Progress Summary */}
            <div className="project-progress-summary">
              <span className="caption font-medium text-secondary uppercase">
                Active Projects Progress
              </span>
              <div className="project-progress-list">
                {projects.slice(0, 4).map((proj) => {
                  const projTasks = tasks.filter((t) => t.project === proj.id);
                  const projTotal = projTasks.length;
                  const projCompleted = projTasks.filter((t) => t.status === 'COMPLETED').length;
                  const projPct = projTotal > 0 ? Math.round((projCompleted / projTotal) * 100) : 0;

                  return (
                    <div key={proj.id} className="project-mini-row">
                      <div className="proj-mini-head">
                        <Link to={`/projects/${proj.id}`} className="proj-mini-name">
                          {proj.name}
                        </Link>
                        <span className="caption text-muted">
                          {projCompleted}/{projTotal} tasks ({projPct}%)
                        </span>
                      </div>
                      <div className="proj-mini-track">
                        <div
                          className="proj-mini-fill"
                          style={{ width: `${projPct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Drill-down Task Table Section */}
      <div className="card analytics-drilldown-card mt-4">
        <div className="section-head">
          <div>
            <h2 className="section-heading">
              {selectedStatusFilter === 'ALL'
                ? 'All Tasks'
                : `${selectedStatusFilter.replace('_', ' ')} Tasks`}
            </h2>
            <p className="caption text-secondary">
              Showing {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
              {selectedStatusFilter !== 'ALL' && ' matching selected chart slice'}
            </p>
          </div>

          <div className="tab-group">
            <button
              className={`tab-btn ${selectedStatusFilter === 'ALL' ? 'active' : ''}`}
              onClick={() => setSelectedStatusFilter('ALL')}
            >
              All ({totalTasks})
            </button>
            <button
              className={`tab-btn ${selectedStatusFilter === 'TODO' ? 'active' : ''}`}
              onClick={() => setSelectedStatusFilter('TODO')}
            >
              To Do ({todoCount})
            </button>
            <button
              className={`tab-btn ${selectedStatusFilter === 'IN_PROGRESS' ? 'active' : ''}`}
              onClick={() => setSelectedStatusFilter('IN_PROGRESS')}
            >
              In Progress ({inProgressCount})
            </button>
            <button
              className={`tab-btn ${selectedStatusFilter === 'BLOCKED' ? 'active' : ''}`}
              onClick={() => setSelectedStatusFilter('BLOCKED')}
            >
              Blocked ({blockedCount})
            </button>
            <button
              className={`tab-btn ${selectedStatusFilter === 'COMPLETED' ? 'active' : ''}`}
              onClick={() => setSelectedStatusFilter('COMPLETED')}
            >
              Completed ({completedCount})
            </button>
          </div>
        </div>

        {filteredTasks.length === 0 ? (
          <div className="empty-subtle">
            <p className="caption text-muted">No tasks found for this status.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: '80px' }}>ID</th>
                  <th>Task Title</th>
                  <th style={{ width: '130px' }}>Status</th>
                  <th style={{ width: '110px' }}>Priority</th>
                  <th style={{ width: '160px' }}>Project</th>
                  <th style={{ width: '140px' }}>Assignee</th>
                  <th style={{ width: '80px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTasks.map((task) => (
                  <tr key={task.id}>
                    <td className="font-mono text-muted">#{task.id}</td>
                    <td>
                      <Link to={`/tasks/${task.id}`} className="table-title-link">
                        {task.title}
                      </Link>
                    </td>
                    <td>
                      {canEdit ? (
                        <select
                          className="select select-xs"
                          value={task.status}
                          onChange={(e) => onStatusChange(task.id, e.target.value)}
                        >
                          <option value="TODO">To Do</option>
                          <option value="IN_PROGRESS">In Progress</option>
                          <option value="BLOCKED">Blocked</option>
                          <option value="COMPLETED">Completed</option>
                        </select>
                      ) : (
                        <StatusBadge status={task.status} />
                      )}
                    </td>
                    <td>
                      <PriorityBadge priority={task.priority} />
                    </td>
                    <td className="caption text-secondary">
                      {task.project_name || '—'}
                    </td>
                    <td className="caption text-secondary">
                      {task.assigned_to_username || 'Unassigned'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/tasks/${task.id}`} className="btn-icon" title="View Details">
                        <ArrowRightIcon size={14} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

