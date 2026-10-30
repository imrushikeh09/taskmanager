import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { tasksApi } from '../api/tasks';
import { projectsApi } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import StatusBadge from '../components/common/StatusBadge';
import PriorityBadge from '../components/common/PriorityBadge';
import TaskAttachments from '../components/tasks/TaskAttachments';
import TaskFormModal from '../components/tasks/TaskFormModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';
import { EditIcon, TrashIcon, CalendarIcon, UserIcon, FolderIcon } from '../components/common/Icons';

export default function TaskDetailPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const { canEdit } = useAuth();

  const [task, setTask] = useState(null);
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const loadTask = useCallback(async () => {
    if (!taskId) return;
    try {
      setIsLoading(true);
      const data = await tasksApi.getTask(taskId);
      setTask(data);

      projectsApi.listProjects().then((res) => {
        setProjects(res.results || (Array.isArray(res) ? res : []));
      }).catch(() => null);
    } catch (err) {
      console.error('Failed to load task details:', err);
      setToast({ message: err.message || 'Task not found.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    loadTask();
  }, [loadTask]);

  const handleStatusChange = async (newStatus) => {
    if (!task) return;
    try {
      setTask((prev) => ({ ...prev, status: newStatus }));
      await tasksApi.updateTask(task.id, { status: newStatus });
      setToast({
        message: `Status updated to ${newStatus.replace('_', ' ')}.`,
        type: 'success',
      });
    } catch (err) {
      setToast({ message: err.message || 'Failed to update status.', type: 'error' });
      loadTask();
    }
  };

  const handleUpdateTask = async (payload) => {
    try {
      const updated = await tasksApi.updateTask(task.id, payload);
      setTask(updated);
      setToast({ message: 'Task updated.', type: 'success' });
    } catch (err) {
      throw err;
    }
  };

  const handleDeleteTask = async () => {
    if (!window.confirm(`Delete task #${task.id}: "${task.title}"?`)) {
      return;
    }
    try {
      await tasksApi.deleteTask(task.id);
      navigate('/tasks', { replace: true });
    } catch (err) {
      setToast({ message: err.message || 'Failed to delete task.', type: 'error' });
    }
  };

  if (isLoading) {
    return (
      <div className="page-shell">
        <LoadingSpinner text={`Loading task #${taskId}...`} />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="page-shell">
        <div className="empty-subtle">
          <h2>Task Not Found</h2>
          <p className="caption text-muted">The task with ID #{taskId} does not exist.</p>
          <Link to="/tasks" className="btn btn-secondary mt-3">
            Back to Tasks
          </Link>
        </div>
      </div>
    );
  }

  const isOverdue =
    task.due_date &&
    task.status !== 'COMPLETED' &&
    new Date(task.due_date) < new Date(new Date().setHours(0, 0, 0, 0));

  return (
    <div className="page-shell">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Breadcrumb */}
      <div className="breadcrumb">
        <Link to="/tasks" className="breadcrumb-item">Tasks</Link>
        <span className="breadcrumb-separator">/</span>
        {task.project && (
          <>
            <Link to={`/projects/${task.project}`} className="breadcrumb-item">
              {task.project_name || `Project #${task.project}`}
            </Link>
            <span className="breadcrumb-separator">/</span>
          </>
        )}
        <span className="breadcrumb-item current">#{task.id}</span>
      </div>

      {/* Main Task View */}
      <div className="card task-detail-card">
        {/* Header */}
        <div className="task-detail-header">
          <div className="task-title-wrap">
            <span className="task-id">#{task.id}</span>
            <h1 className="task-detail-title">{task.title}</h1>
          </div>

          <div className="task-detail-actions">
            <StatusBadge status={task.status} />
            <PriorityBadge priority={task.priority} />
            {canEdit && (
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setIsEditModalOpen(true)}
              >
                <EditIcon size={13} />
                <span>Edit</span>
              </button>
            )}
          </div>
        </div>

        {/* Status switcher bar */}
        {canEdit && (
          <div className="status-flow-bar">
            <span className="caption font-medium text-muted">Status:</span>
            <div className="status-flow-buttons">
              <button
                className={`btn btn-sm ${task.status === 'TODO' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => handleStatusChange('TODO')}
                disabled={task.status === 'TODO'}
              >
                To Do
              </button>
              <button
                className={`btn btn-sm ${task.status === 'IN_PROGRESS' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => handleStatusChange('IN_PROGRESS')}
                disabled={task.status === 'IN_PROGRESS'}
              >
                In Progress
              </button>
              <button
                className={`btn btn-sm ${task.status === 'BLOCKED' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => handleStatusChange('BLOCKED')}
                disabled={task.status === 'BLOCKED'}
              >
                Blocked
              </button>
              <button
                className={`btn btn-sm ${task.status === 'COMPLETED' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => handleStatusChange('COMPLETED')}
                disabled={task.status === 'COMPLETED'}
              >
                Completed
              </button>
            </div>
          </div>
        )}

        {/* Content Layout */}
        <div className="detail-columns">
          {/* Main content: Description + Attachments */}
          <div className="detail-primary">
            <div className="section-block">
              <h4 className="section-title">Description</h4>
              <div className="task-description-body">
                {task.description ? (
                  <p>{task.description}</p>
                ) : (
                  <p className="text-muted fst-italic">No description provided.</p>
                )}
              </div>
            </div>

            <TaskAttachments taskId={task.id} canEdit={canEdit} />
          </div>

          {/* Sidebar Metadata */}
          <div className="detail-sidebar">
            <div className="meta-card">
              <h4 className="meta-card-title">Properties</h4>

              <div className="meta-row">
                <span className="meta-label">Project</span>
                <span className="meta-value">
                  {task.project ? (
                    <Link to={`/projects/${task.project}`} className="link-subtle">
                      <FolderIcon size={13} />
                      <span>{task.project_name || `Project #${task.project}`}</span>
                    </Link>
                  ) : (
                    '—'
                  )}
                </span>
              </div>

              <div className="meta-row">
                <span className="meta-label">Assignee</span>
                <span className="meta-value">
                  <UserIcon size={13} />
                  <span>{task.assignee_username || 'Unassigned'}</span>
                </span>
              </div>

              <div className="meta-row">
                <span className="meta-label">Creator</span>
                <span className="meta-value">
                  <UserIcon size={13} />
                  <span>{task.creator_username || 'System'}</span>
                </span>
              </div>

              <div className="meta-row">
                <span className="meta-label">Due Date</span>
                <span className={`meta-value ${isOverdue ? 'text-danger font-medium' : ''}`}>
                  <CalendarIcon size={13} />
                  <span>{task.due_date || 'None'}</span>
                  {isOverdue && <span className="badge badge-danger ml-1">Overdue</span>}
                </span>
              </div>

              <div className="meta-row">
                <span className="meta-label">Created</span>
                <span className="meta-value text-muted">
                  {new Date(task.created_at).toLocaleDateString()}
                </span>
              </div>

              <div className="meta-row">
                <span className="meta-label">Updated</span>
                <span className="meta-value text-muted">
                  {new Date(task.updated_at).toLocaleDateString()}
                </span>
              </div>

              {canEdit && (
                <div className="meta-danger-zone">
                  <button onClick={handleDeleteTask} className="btn btn-danger btn-sm btn-block">
                    <TrashIcon size={13} />
                    <span>Delete Task</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditModalOpen && (
        <TaskFormModal
          isOpen={isEditModalOpen}
          onClose={() => setIsEditModalOpen(false)}
          onSubmit={handleUpdateTask}
          initialData={task}
          projects={projects}
        />
      )}
    </div>
  );
}
