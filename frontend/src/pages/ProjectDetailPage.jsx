import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectsApi } from '../api/projects';
import { tasksApi } from '../api/tasks';
import { useAuth } from '../context/AuthContext';
import ProjectStatsCard from '../components/projects/ProjectStatsCard';
import TaskTable from '../components/tasks/TaskTable';
import TaskCard from '../components/tasks/TaskCard';
import TaskFormModal from '../components/tasks/TaskFormModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Toast from '../components/common/Toast';
import { PlusIcon, KanbanIcon, ListIcon, FolderIcon, UserIcon } from '../components/common/Icons';

const COLUMNS = [
  { id: 'TODO', title: 'To Do', colorDot: 'dot-todo' },
  { id: 'IN_PROGRESS', title: 'In Progress', colorDot: 'dot-in-progress' },
  { id: 'BLOCKED', title: 'Blocked', colorDot: 'dot-blocked' },
  { id: 'COMPLETED', title: 'Completed', colorDot: 'dot-completed' },
];

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const { canEdit } = useAuth();

  const [project, setProject] = useState(null);
  const [stats, setStats] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [activeTab, setActiveTab] = useState('kanban'); // 'kanban' or 'table'
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);

  const loadProjectData = useCallback(async () => {
    if (!projectId) return;
    try {
      setIsLoading(true);
      const [projRes, statsRes, tasksRes] = await Promise.all([
        projectsApi.getProject(projectId),
        projectsApi.getProjectStats(projectId).catch(() => null),
        tasksApi.listTasks({ project: projectId, page_size: 100 }),
      ]);

      setProject(projRes);
      setStats(statsRes);
      setTasks(tasksRes.results || (Array.isArray(tasksRes) ? tasksRes : []));

      projectsApi
        .getProjectPerformance(projectId)
        .then((perf) => setPerformance(perf))
        .catch(() => null);
    } catch (err) {
      console.error('Failed to load project details:', err);
      setToast({ message: err.message || 'Project not found.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    loadProjectData();
  }, [loadProjectData]);

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      await tasksApi.updateTask(taskId, { status: newStatus });
      setToast({ message: `Task #${taskId} moved to ${newStatus}.`, type: 'success' });
      projectsApi.getProjectStats(projectId).then(setStats).catch(() => null);
    } catch (err) {
      setToast({ message: err.message || 'Failed to update status.', type: 'error' });
      loadProjectData();
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm(`Delete task #${taskId}?`)) return;
    try {
      await tasksApi.deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      setToast({ message: `Task #${taskId} deleted.`, type: 'success' });
      projectsApi.getProjectStats(projectId).then(setStats).catch(() => null);
    } catch (err) {
      setToast({ message: err.message || 'Failed to delete task.', type: 'error' });
    }
  };

  const handleCreateTask = async (payload) => {
    await tasksApi.createTask({
      ...payload,
      project_id: parseInt(projectId, 10),
    });
    setToast({ message: 'Task created.', type: 'success' });
    loadProjectData();
  };

  if (isLoading) {
    return (
      <div className="page-shell">
        <LoadingSpinner text="Loading project details..." />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="page-shell">
        <div className="empty-subtle">
          <h2>Project Not Found</h2>
          <p className="caption text-muted">The requested project does not exist.</p>
          <Link to="/projects" className="btn btn-secondary mt-3">
            Back to Projects
          </Link>
        </div>
      </div>
    );
  }

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
        <Link to="/projects" className="breadcrumb-item">Projects</Link>
        <span className="breadcrumb-separator">/</span>
        <span className="breadcrumb-item current">{project.name}</span>
      </div>

      {/* Project Overview Card */}
      <div className="card project-header-card">
        <div className="project-header-top">
          <div className="project-headline">
            <div className="project-avatar">
              <FolderIcon size={18} />
            </div>
            <div>
              <h1 className="project-name-main">{project.name}</h1>
              {project.description && (
                <p className="project-desc-main">{project.description}</p>
              )}
            </div>
          </div>

          <div className="project-header-meta">
            <div className="meta-pill">
              <UserIcon size={13} />
              <span>{project.owner_username || 'Owner'}</span>
            </div>
            <div className="meta-pill">
              <span>{tasks.length} total tasks</span>
            </div>
          </div>
        </div>

        {stats && <ProjectStatsCard stats={stats} performance={performance} />}
      </div>

      {/* Views Toolbar */}
      <div className="toolbar-row">
        <div className="segmented-control">
          <button
            className={`seg-btn ${activeTab === 'kanban' ? 'active' : ''}`}
            onClick={() => setActiveTab('kanban')}
          >
            <KanbanIcon size={14} />
            <span>Board</span>
          </button>
          <button
            className={`seg-btn ${activeTab === 'table' ? 'active' : ''}`}
            onClick={() => setActiveTab('table')}
          >
            <ListIcon size={14} />
            <span>Tasks ({tasks.length})</span>
          </button>
        </div>

        {canEdit && (
          <button className="btn btn-primary" onClick={() => setIsTaskModalOpen(true)}>
            <PlusIcon size={14} />
            <span>Add Task</span>
          </button>
        )}
      </div>

      {/* Content */}
      {activeTab === 'kanban' ? (
        <div className="board-grid">
          {COLUMNS.map((col) => {
            const colTasks = tasks.filter((t) => t.status === col.id);
            return (
              <div key={col.id} className="board-column">
                <div className="column-header">
                  <div className="column-title-group">
                    <span className={`status-dot ${col.colorDot}`}></span>
                    <span className="column-title">{col.title}</span>
                  </div>
                  <span className="column-counter">{colTasks.length}</span>
                </div>

                <div className="column-cards">
                  {colTasks.length === 0 ? (
                    <div className="column-empty">No tasks</div>
                  ) : (
                    colTasks.map((task) => (
                      <TaskCard
                        key={task.id}
                        task={task}
                        onStatusChange={handleStatusChange}
                        canEdit={canEdit}
                      />
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card">
          <TaskTable
            tasks={tasks}
            onStatusChange={handleStatusChange}
            onDelete={handleDeleteTask}
            canEdit={canEdit}
          />
        </div>
      )}

      {/* Task Creation Modal */}
      {isTaskModalOpen && (
        <TaskFormModal
          isOpen={isTaskModalOpen}
          onClose={() => setIsTaskModalOpen(false)}
          onSubmit={handleCreateTask}
          initialData={{ project_id: parseInt(projectId, 10), project_name: project.name }}
          projects={[project]}
        />
      )}
    </div>
  );
}
