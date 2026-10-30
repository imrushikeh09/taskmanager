import React from 'react';
import { Link } from 'react-router-dom';
import { FolderIcon, UserIcon, EditIcon, TrashIcon } from '../common/Icons';

export default function ProjectCard({ project, onEdit, onDelete, canManage = false }) {
  return (
    <div className="card project-card">
      <div className="project-card-header">
        <div className="project-title-area">
          <div className="project-avatar">
            <FolderIcon size={16} />
          </div>
          <Link to={`/projects/${project.id}`} className="project-name-link">
            <h3 className="project-name">{project.name}</h3>
          </Link>
        </div>

        {canManage && (
          <div className="project-card-actions">
            {onEdit && (
              <button
                onClick={() => onEdit(project)}
                className="btn-icon"
                title="Edit Project"
              >
                <EditIcon size={14} />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(project.id)}
                className="btn-icon btn-icon-danger"
                title="Delete Project"
              >
                <TrashIcon size={14} />
              </button>
            )}
          </div>
        )}
      </div>

      <p className="project-desc">
        {project.description || 'No description provided.'}
      </p>

      <div className="project-card-footer">
        <div className="project-owner">
          <UserIcon size={13} />
          <span>{project.owner_username || 'Owner'}</span>
        </div>
        <span className="badge badge-subtle">
          {project.task_count ?? 0} {project.task_count === 1 ? 'task' : 'tasks'}
        </span>
      </div>
    </div>
  );
}
