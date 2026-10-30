import React, { useState, useEffect, useCallback } from 'react';
import { projectsApi } from '../api/projects';
import { useAuth } from '../context/AuthContext';
import ProjectCard from '../components/projects/ProjectCard';
import ProjectFormModal from '../components/projects/ProjectFormModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import Toast from '../components/common/Toast';
import { SearchIcon, PlusIcon } from '../components/common/Icons';

export default function ProjectsPage() {
  const { user, isAdmin, canEdit } = useAuth();

  const [projects, setProjects] = useState([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const [modalState, setModalState] = useState({
    isOpen: false,
    initialData: null,
  });

  const loadProjects = useCallback(async () => {
    try {
      setIsLoading(true);
      const res = await projectsApi.listProjects({ search });
      setProjects(res.results || (Array.isArray(res) ? res : []));
    } catch (err) {
      console.error('Failed to load projects:', err);
      setToast({ message: err.message || 'Failed to retrieve projects.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [search]);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleCreateOrUpdateProject = async (data) => {
    try {
      if (modalState.initialData?.id) {
        await projectsApi.updateProject(modalState.initialData.id, data);
        setToast({ message: 'Project updated.', type: 'success' });
      } else {
        await projectsApi.createProject(data);
        setToast({ message: 'Project created.', type: 'success' });
      }
      loadProjects();
    } catch (err) {
      throw err;
    }
  };

  const handleDeleteProject = async (id) => {
    if (!window.confirm('Delete this project and all its tasks?')) {
      return;
    }
    try {
      await projectsApi.deleteProject(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
      setToast({ message: 'Project deleted.', type: 'success' });
    } catch (err) {
      setToast({ message: err.message || 'Delete failed. Only the owner can delete.', type: 'error' });
    }
  };

  const handleOpenEdit = (project) => {
    setModalState({
      isOpen: true,
      initialData: project,
    });
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
          <h1 className="page-title">Projects</h1>
          <p className="page-subtitle">
            Organization workspaces, team ownership, and sprint scope.
          </p>
        </div>

        {canEdit && (
          <button
            className="btn btn-primary"
            onClick={() => setModalState({ isOpen: true, initialData: null })}
          >
            <PlusIcon size={14} />
            <span>New Project</span>
          </button>
        )}
      </div>

      {/* Search Bar */}
      <div className="projects-filter-wrap">
        <div className="search-box">
          <SearchIcon size={14} className="search-box-icon" />
          <input
            type="text"
            placeholder="Search projects..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input search-input"
          />
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingSpinner text="Loading projects..." />
      ) : projects.length === 0 ? (
        <EmptyState
          title="No projects found"
          description="Create your first workspace to start organizing tasks."
          action={
            canEdit && (
              <button
                className="btn btn-primary"
                onClick={() => setModalState({ isOpen: true, initialData: null })}
              >
                Create Project
              </button>
            )
          }
        />
      ) : (
        <div className="projects-grid">
          {projects.map((project) => {
            const isOwner = user && (user.id === project.owner || user.username === project.owner_username);
            const canManage = isAdmin || isOwner;

            return (
              <ProjectCard
                key={project.id}
                project={project}
                onEdit={handleOpenEdit}
                onDelete={handleDeleteProject}
                canManage={canManage}
              />
            );
          })}
        </div>
      )}

      {/* Project Form Modal */}
      {modalState.isOpen && (
        <ProjectFormModal
          isOpen={modalState.isOpen}
          onClose={() => setModalState({ isOpen: false, initialData: null })}
          onSubmit={handleCreateOrUpdateProject}
          initialData={modalState.initialData}
        />
      )}
    </div>
  );
}
