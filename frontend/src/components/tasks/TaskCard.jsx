import React from 'react';
import { Link } from 'react-router-dom';
import PriorityBadge from '../common/PriorityBadge';
import { CalendarIcon, FolderIcon } from '../common/Icons';

export default function TaskCard({ task, onStatusChange, canEdit = true }) {
  const isOverdue =
    task.due_date &&
    task.status !== 'COMPLETED' &&
    new Date(task.due_date) < new Date(new Date().setHours(0, 0, 0, 0));

  const handleStatusSelect = (e) => {
    e.stopPropagation();
    e.preventDefault();
    if (onStatusChange) {
      onStatusChange(task.id, e.target.value);
    }
  };

  return (
    <div className={`card task-card ${isOverdue ? 'is-overdue' : ''}`}>
      <div className="task-card-header">
        <span className="task-id">#{task.id}</span>
        <PriorityBadge priority={task.priority} />
      </div>

      <Link to={`/tasks/${task.id}`} className="task-card-title-link">
        <h4 className="task-card-title">{task.title}</h4>
      </Link>

      {task.description && (
        <p className="task-card-desc">
          {task.description.length > 80
            ? `${task.description.substring(0, 80)}...`
            : task.description}
        </p>
      )}

      {task.project_name && (
        <div className="task-card-project">
          <FolderIcon size={12} />
          <span>{task.project_name}</span>
        </div>
      )}

      <div className="task-card-footer">
        <div className="task-assignee">
          <span className="avatar avatar-xs" title={`Assignee: ${task.assignee_username || 'Unassigned'}`}>
            {(task.assignee_username?.[0] || '?').toUpperCase()}
          </span>
          <span className="assignee-name">
            {task.assignee_username || 'Unassigned'}
          </span>
        </div>

        {task.due_date && (
          <span className={`task-due ${isOverdue ? 'text-danger' : ''}`} title="Due date">
            <CalendarIcon size={12} />
            <span>{task.due_date}</span>
          </span>
        )}
      </div>

      {canEdit && onStatusChange && (
        <div className="task-card-quick-actions">
          <select
            value={task.status}
            onChange={handleStatusSelect}
            className="select select-xs"
            title="Move status"
          >
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="BLOCKED">Blocked</option>
            <option value="COMPLETED">Completed</option>
          </select>
        </div>
      )}
    </div>
  );
}
