import React from 'react';
import { Link } from 'react-router-dom';
import StatusBadge from '../common/StatusBadge';
import PriorityBadge from '../common/PriorityBadge';
import { TrashIcon } from '../common/Icons';

export default function TaskTable({
  tasks = [],
  onStatusChange,
  onDelete,
  canEdit = true,
}) {
  return (
    <div className="table-responsive">
      <table className="table">
        <thead>
          <tr>
            <th style={{ width: '70px' }}>ID</th>
            <th>Title</th>
            <th>Project</th>
            <th style={{ width: '90px' }}>Priority</th>
            <th style={{ width: '130px' }}>Status</th>
            <th>Assignee</th>
            <th style={{ width: '110px' }}>Due Date</th>
            <th style={{ width: '50px', textAlign: 'right' }}></th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => {
            const isOverdue =
              task.due_date &&
              task.status !== 'COMPLETED' &&
              new Date(task.due_date) < new Date(new Date().setHours(0, 0, 0, 0));

            return (
              <tr key={task.id} className={isOverdue ? 'row-overdue' : ''}>
                <td>
                  <span className="task-id">#{task.id}</span>
                </td>
                <td className="cell-primary">
                  <Link to={`/tasks/${task.id}`} className="table-title-link">
                    {task.title}
                  </Link>
                  {task.description && (
                    <span className="table-subtext">
                      {task.description.length > 60
                        ? `${task.description.substring(0, 60)}...`
                        : task.description}
                    </span>
                  )}
                </td>
                <td>
                  <span className="text-secondary">
                    {task.project_name || `Project #${task.project}`}
                  </span>
                </td>
                <td>
                  <PriorityBadge priority={task.priority} />
                </td>
                <td>
                  {canEdit && onStatusChange ? (
                    <select
                      value={task.status}
                      onChange={(e) => onStatusChange(task.id, e.target.value)}
                      className="select select-xs"
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
                  <div className="assignee-cell">
                    <span className="avatar avatar-xs">
                      {(task.assignee_username?.[0] || '?').toUpperCase()}
                    </span>
                    <span className="text-secondary">{task.assignee_username || 'Unassigned'}</span>
                  </div>
                </td>
                <td>
                  <span className={`cell-date ${isOverdue ? 'text-danger font-medium' : 'text-secondary'}`}>
                    {task.due_date || '—'}
                  </span>
                </td>
                <td style={{ textAlign: 'right' }}>
                  {canEdit && onDelete && (
                    <button
                      onClick={() => onDelete(task.id)}
                      className="btn-icon btn-icon-danger"
                      title="Delete task"
                      aria-label="Delete task"
                    >
                      <TrashIcon size={14} />
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
