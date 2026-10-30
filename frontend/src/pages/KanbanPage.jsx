import React, { useState, useEffect, useCallback } from 'react';
import { tasksApi } from '../api/tasks';
import { projectsApi } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import TaskCard from '../components/tasks/TaskCard';
import TaskFormModal from '../components/tasks/TaskFormModal';
import AnalyticsCharts from '../components/analytics/AnalyticsCharts';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';
import { PlusIcon, KanbanIcon, PieChartIcon } from '../components/common/Icons';

const COLUMNS = [
  { id: 'TODO', title: 'To Do', colorDot: 'dot-todo' },
  { id: 'IN_PROGRESS', title: 'In Progress', colorDot: 'dot-in-progress' },
  { id: 'BLOCKED', title: 'Blocked', colorDot: 'dot-blocked' },
  { id: 'COMPLETED', title: 'Completed', colorDot: 'dot-completed' },
];

export default function KanbanPage() {
  const { canEdit } = useAuth();

  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [viewMode, setViewMode] = useState('board'); // 'board' | 'analytics'
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const [modalState, setModalState] = useState({
    isOpen: false,
    initialStatus: 'TODO',
  });

  const loadData = useCallback(async () => {
    try {
      setIsLoading(true);
      const params = { page_size: 100 };
      if (selectedProject) params.project = selectedProject;

      const [tasksRes, projectsRes] = await Promise.all([
        tasksApi.listTasks(params),
        projectsApi.listProjects(),
      ]);

      setTasks(tasksRes.results || (Array.isArray(tasksRes) ? tasksRes : []));
      setProjects(projectsRes.results || (Array.isArray(projectsRes) ? projectsRes : []));
    } catch (err) {
      console.error('Failed to load board tasks:', err);
      setToast({ message: err.message || 'Could not load tasks.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [selectedProject]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      await tasksApi.updateTask(taskId, { status: newStatus });
      setToast({
        message: `Task #${taskId} moved to ${newStatus.replace('_', ' ')}.`,
        type: 'success',
      });
    } catch (err) {
      setToast({ message: err.message || 'Failed to move task.', type: 'error' });
      loadData();
    }
  };

  const handleOpenCreateModal = (columnStatus = 'TODO') => {
    setModalState({
      isOpen: true,
      initialStatus: columnStatus,
    });
  };

  const handleCreateTask = async (payload) => {
    await tasksApi.createTask(payload);
    setToast({ message: 'Task created.', type: 'success' });
    loadData();
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
          <h1 className="page-title">{viewMode === 'board' ? 'Board' : 'Visual Analytics'}</h1>
          <p className="page-subtitle">
            {viewMode === 'board'
              ? 'Visual workflow across task lifecycle stages.'
              : 'Interactive graphs, status distribution, and workload insights.'}
          </p>
        </div>

        <div className="page-actions">
          {/* Segmented View Switcher */}
          <div className="segmented-control">
            <button
              className={`tab-btn ${viewMode === 'board' ? 'active' : ''}`}
              onClick={() => setViewMode('board')}
              title="Kanban Board view"
            >
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <KanbanIcon size={13} />
                <span>Board</span>
              </span>
            </button>
            <button
              className={`tab-btn ${viewMode === 'analytics' ? 'active' : ''}`}
              onClick={() => setViewMode('analytics')}
              title="Graphs and visual metrics"
            >
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}>
                <PieChartIcon size={13} />
                <span>Analytics</span>
              </span>
            </button>
          </div>

          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="select"
          >
            <option value="">All Projects ({projects.length})</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>

          {canEdit && (
            <button
              className="btn btn-primary"
              onClick={() => handleOpenCreateModal('TODO')}
            >
              <PlusIcon size={14} />
              <span>Add Task</span>
            </button>
          )}
        </div>
      </div>

      {/* Content: Board or Visual Analytics */}
      {isLoading ? (
        <LoadingSpinner text="Loading workspace data..." />
      ) : viewMode === 'analytics' ? (
        <AnalyticsCharts
          tasks={tasks}
          projects={projects}
          onStatusChange={handleStatusChange}
          canEdit={canEdit}
        />
      ) : (
        <div className="board-grid">
          {COLUMNS.map((col) => {
            const columnTasks = tasks.filter((t) => t.status === col.id);

            return (
              <div key={col.id} className="board-column">
                <div className="column-header">
                  <div className="column-title-group">
                    <span className={`status-dot ${col.colorDot}`}></span>
                    <span className="column-title">{col.title}</span>
                  </div>
                  <span className="column-counter">{columnTasks.length}</span>
                </div>

                <div className="column-cards">
                  {columnTasks.length === 0 ? (
                    <div className="column-empty">No tasks</div>
                  ) : (
                    columnTasks.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onStatusChange={handleStatusChange}
                        canEdit={canEdit}
                      />
                    ))
                  )}
                </div>

                {canEdit && (
                  <button
                    className="btn btn-ghost btn-xs btn-column-add"
                    onClick={() => handleOpenCreateModal(col.id)}
                  >
                    <PlusIcon size={12} />
                    <span>Add task</span>
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Task Creation Modal */}
      {modalState.isOpen && (
        <TaskFormModal
          isOpen={modalState.isOpen}
          onClose={() => setModalState({ isOpen: false, initialStatus: 'TODO' })}
          onSubmit={handleCreateTask}
          initialData={{
            status: modalState.initialStatus,
            project_id: selectedProject ? parseInt(selectedProject, 10) : undefined,
          }}
          projects={projects}
        />
      )}
    </div>
  );
}
