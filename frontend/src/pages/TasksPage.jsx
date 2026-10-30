import React, { useState, useEffect, useCallback } from 'react';
import { tasksApi } from '../api/tasks';
import { projectsApi } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import TaskFilterBar from '../components/tasks/TaskFilterBar';
import TaskTable from '../components/tasks/TaskTable';
import TaskCard from '../components/tasks/TaskCard';
import TaskFormModal from '../components/tasks/TaskFormModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import Toast from '../components/common/Toast';
import { ListIcon, KanbanIcon } from '../components/common/Icons';

export default function TasksPage() {
  const { canEdit } = useAuth();

  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'grid'
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const [filters, setFilters] = useState({
    search: '',
    project: '',
    status: '',
    priority: '',
    ordering: '-created_at',
  });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const loadProjects = useCallback(async () => {
    try {
      const res = await projectsApi.listProjects();
      setProjects(res.results || (Array.isArray(res) ? res : []));
    } catch (err) {
      console.error('Failed to load projects list:', err);
    }
  }, []);

  const loadTasks = useCallback(async () => {
    try {
      setIsLoading(true);
      const params = {
        page,
        page_size: 20,
        ordering: filters.ordering,
      };
      if (filters.search) params.search = filters.search;
      if (filters.project) params.project = filters.project;
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;

      const res = await tasksApi.listTasks(params);
      const items = res.results || (Array.isArray(res) ? res : []);
      setTasks(items);
      setTotalCount(res.count ?? items.length);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setToast({ message: err.message || 'Failed to fetch tasks.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      await tasksApi.updateTask(taskId, { status: newStatus });
      setToast({ message: `Task #${taskId} updated to ${newStatus.replace('_', ' ')}.`, type: 'success' });
    } catch (err) {
      setToast({ message: err.message || 'Failed to update status.', type: 'error' });
      loadTasks();
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
    loadTasks();
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(1);
  };

  const handleResetFilters = () => {
    setFilters({
      search: '',
      project: '',
      status: '',
      priority: '',
      ordering: '-created_at',
    });
    setPage(1);
  };

  const totalPages = Math.ceil(totalCount / 20) || 1;

  return (
    <div className="page-shell">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Tasks</h1>
          <p className="page-subtitle">
            All tasks across projects. Filter by assignee, status, or due date.
          </p>
        </div>

        <div className="segmented-control">
          <button
            className={`seg-btn ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
            title="Table View"
          >
            <ListIcon size={14} />
            <span>Table</span>
          </button>
          <button
            className={`seg-btn ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
            title="Card Grid View"
          >
            <KanbanIcon size={14} />
            <span>Cards</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <TaskFilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        projects={projects}
        onReset={handleResetFilters}
        onNewTask={() => setIsCreateModalOpen(true)}
        canCreate={canEdit}
      />

      {/* Tasks Content */}
      {isLoading ? (
        <LoadingSpinner text="Retrieving tasks..." />
      ) : tasks.length === 0 ? (
        <EmptyState
          title="No tasks found"
          description="Try adjusting your filters or create a new task."
          action={
            canEdit && (
              <button
                className="btn btn-primary"
                onClick={() => setIsCreateModalOpen(true)}
              >
                Create Task
              </button>
            )
          }
        />
      ) : viewMode === 'table' ? (
        <TaskTable
          tasks={tasks}
          onStatusChange={handleStatusChange}
          onDelete={handleDeleteTask}
          canEdit={canEdit}
        />
      ) : (
        <div className="task-cards-grid">
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onStatusChange={handleStatusChange}
              canEdit={canEdit}
            />
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="pagination">
          <span className="caption text-muted">
            Page {page} of {totalPages} ({totalCount} total)
          </span>
          <div className="pagination-actions">
            <button
              className="btn btn-secondary btn-sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <button
              className="btn btn-secondary btn-sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {isCreateModalOpen && (
        <TaskFormModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreateTask}
          projects={projects}
        />
      )}
    </div>
  );
}
