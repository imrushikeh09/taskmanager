import React from 'react';
import { SearchIcon, PlusIcon, XIcon } from '../common/Icons';

export default function TaskFilterBar({
  filters,
  onFilterChange,
  projects = [],
  onReset,
  onNewTask,
  canCreate = true,
}) {
  const hasActiveFilters = Boolean(
    filters.search || filters.project || filters.status || filters.priority
  );

  return (
    <div className="filter-bar">
      <div className="filter-controls">
        {/* Search */}
        <div className="search-box">
          <SearchIcon size={14} className="search-box-icon" />
          <input
            type="text"
            placeholder="Search tasks..."
            value={filters.search || ''}
            onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
            className="input search-input"
          />
        </div>

        {/* Project Selector */}
        <select
          value={filters.project || ''}
          onChange={(e) => onFilterChange({ ...filters, project: e.target.value })}
          className="select"
        >
          <option value="">All Projects</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>

        {/* Status Selector */}
        <select
          value={filters.status || ''}
          onChange={(e) => onFilterChange({ ...filters, status: e.target.value })}
          className="select"
        >
          <option value="">All Statuses</option>
          <option value="TODO">To Do</option>
          <option value="IN_PROGRESS">In Progress</option>
          <option value="BLOCKED">Blocked</option>
          <option value="COMPLETED">Completed</option>
        </select>

        {/* Priority Selector */}
        <select
          value={filters.priority || ''}
          onChange={(e) => onFilterChange({ ...filters, priority: e.target.value })}
          className="select"
        >
          <option value="">All Priorities</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="URGENT">Urgent</option>
        </select>

        {/* Ordering Selector */}
        <select
          value={filters.ordering || '-created_at'}
          onChange={(e) => onFilterChange({ ...filters, ordering: e.target.value })}
          className="select"
        >
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="due_date">Due Date</option>
          <option value="-priority">Priority</option>
        </select>

        {/* Reset button */}
        {hasActiveFilters && (
          <button className="btn btn-ghost btn-sm" onClick={onReset} title="Clear filters">
            <XIcon size={13} />
            <span>Clear</span>
          </button>
        )}
      </div>

      {canCreate && onNewTask && (
        <button className="btn btn-primary" onClick={onNewTask}>
          <PlusIcon size={14} />
          <span>New Task</span>
        </button>
      )}
    </div>
  );
}
