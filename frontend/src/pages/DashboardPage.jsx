import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { tasksApi } from '../api/tasks';
import { projectsApi } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import TaskTable from '../components/tasks/TaskTable';
import TaskFormModal from '../components/tasks/TaskFormModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';
import { PlusIcon, ArrowRightIcon, FolderIcon } from '../components/common/Icons';

export default function DashboardPage() {
  const { user, canEdit } = useAuth();

  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [toast, setToast] = useState(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);

  const loadDashboardData = useCallback(async () => {
    try {
      setIsLoading(true);
      const [tasksRes, projectsRes] = await Promise.all([
        tasksApi.listTasks({ page_size: 50 }),
        projectsApi.listProjects(),
      ]);

      const taskList = tasksRes.results || (Array.isArray(tasksRes) ? tasksRes : []);
      const projList = projectsRes.results || (Array.isArray(projectsRes) ? projectsRes : []);

      setTasks(taskList);
      setProjects(projList);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setToast({ message: err.message || 'Failed to load workspace data.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Aggregate metrics
  const totalTasks = tasks.length;
  const inProgressCount = tasks.filter((t) => t.status === 'IN_PROGRESS').length;
  const blockedCount = tasks.filter((t) => t.status === 'BLOCKED').length;
  const completedCount = tasks.filter((t) => t.status === 'COMPLETED').length;
  const urgentCount = tasks.filter((t) => t.priority === 'URGENT' || t.priority === 'HIGH').length;
  const completionRate = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  // Filter tasks for table
  const displayedTasks = tasks.filter((t) => {
    if (filter === 'ALL') return true;
    return t.status === filter;
  });

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      await tasksApi.updateTask(taskId, { status: newStatus });
      setToast({ message: `Task #${taskId} updated to ${newStatus.replace('_', ' ')}.`, type: 'success' });
    } catch (err) {
      setToast({ message: err.message || 'Status update failed.', type: 'error' });
      loadDashboardData();
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm(`Delete task #${taskId}?`)) return;
    try {
      await tasksApi.deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      setToast({ message: `Task #${taskId} deleted.`, type: 'success' });
    } catch (err) {
      setToast({ message: err.message || 'Failed to delete task.', type: 'error' });
    }
  };

  const handleCreateTask = async (payload) => {
    await tasksApi.createTask(payload);
    setToast({ message: 'Task created.', type: 'success' });
    loadDashboardData();
  };

  return (
    <div className="page-shell">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Workspace</h1>
          <p className="page-subtitle">
            Welcome back, {user?.first_name || user?.username || 'team member'}. Here is your current sprint progress.
          </p>
        </div>
        <div className="page-actions">
          <Link to="/kanban" className="btn btn-secondary">
            Board
          </Link>
          {canEdit && (
            <button className="btn btn-primary" onClick={() => setIsTaskModalOpen(true)}>
              <PlusIcon size={14} />
              <span>New Task</span>
            </button>
          )}
        </div>
      </div>

      {/* Metric Cards */}
      <div className="metric-cards-grid">
        <div className="card metric-card">
          <span className="metric-title">Total Tasks</span>
          <span className="metric-value">{totalTasks}</span>
          <span className="caption text-muted">Across {projects.length} projects</span>
        </div>

        <div className="card metric-card">
          <span className="metric-title">In Progress</span>
          <span className="metric-value text-info">{inProgressCount}</span>
          <span className="caption text-muted">Currently active</span>
        </div>

        <div className="card metric-card">
          <span className="metric-title">Blocked</span>
          <span className="metric-value text-danger">{blockedCount}</span>
          <span className="caption text-muted">Needs attention</span>
        </div>

        <div className="card metric-card">
          <span className="metric-title">Completed</span>
          <span className="metric-value text-success">{completedCount}</span>
          <span className="caption text-muted">{completionRate}% sprint progress</span>
        </div>

        <div className="card metric-card">
          <span className="metric-title">High & Urgent</span>
          <span className="metric-value text-warning">{urgentCount}</span>
          <span className="caption text-muted">Top priority issues</span>
        </div>
      </div>

      {/* Active Projects Snapshot */}
      <div className="card dashboard-section">
        <div className="section-head">
          <div>
            <h2 className="section-heading">Projects</h2>
            <p className="caption text-muted">Recent project repositories</p>
          </div>
          <Link to="/projects" className="link-subtle">
            <span>View all</span>
            <ArrowRightIcon size={13} />
          </Link>
        </div>

        <div className="projects-compact-grid">
          {projects.slice(0, 3).map((proj) => (
            <Link key={proj.id} to={`/projects/${proj.id}`} className="project-compact-card">
              <div className="proj-compact-icon">
                <FolderIcon size={16} />
              </div>
              <div className="proj-compact-details">
                <span className="proj-compact-name">{proj.name}</span>
                <span className="caption text-muted">
                  {proj.task_count ?? 0} {proj.task_count === 1 ? 'task' : 'tasks'}
                </span>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Tasks Table Section */}
      <div className="card dashboard-section">
        <div className="section-head">
          <div>
            <h2 className="section-heading">Active Tasks</h2>
            <p className="caption text-muted">{displayedTasks.length} tasks matching current filter</p>
          </div>

          <div className="tab-group">
            <button
              className={`tab-btn ${filter === 'ALL' ? 'active' : ''}`}
              onClick={() => setFilter('ALL')}
            >
              All ({totalTasks})
            </button>
            <button
              className={`tab-btn ${filter === 'IN_PROGRESS' ? 'active' : ''}`}
              onClick={() => setFilter('IN_PROGRESS')}
            >
              In Progress ({inProgressCount})
            </button>
            <button
              className={`tab-btn ${filter === 'BLOCKED' ? 'active' : ''}`}
              onClick={() => setFilter('BLOCKED')}
            >
              Blocked ({blockedCount})
            </button>
            <button
              className={`tab-btn ${filter === 'TODO' ? 'active' : ''}`}
              onClick={() => setFilter('TODO')}
            >
              To Do ({tasks.filter((t) => t.status === 'TODO').length})
            </button>
            <button
              className={`tab-btn ${filter === 'COMPLETED' ? 'active' : ''}`}
              onClick={() => setFilter('COMPLETED')}
            >
              Completed ({completedCount})
            </button>
          </div>
        </div>

        {isLoading ? (
          <LoadingSpinner text="Loading tasks..." />
        ) : displayedTasks.length === 0 ? (
          <div className="empty-subtle">
            <p>No tasks match this filter</p>
          </div>
        ) : (
          <TaskTable
            tasks={displayedTasks}
            onStatusChange={handleStatusChange}
            onDelete={handleDeleteTask}
            canEdit={canEdit}
          />
        )}
      </div>

      {/* Task Creation Modal */}
      {isTaskModalOpen && (
        <TaskFormModal
          isOpen={isTaskModalOpen}
          onClose={() => setIsTaskModalOpen(false)}
          onSubmit={handleCreateTask}
          projects={projects}
        />
      )}
    </div>
  );
}
