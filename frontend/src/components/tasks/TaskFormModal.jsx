import React, { useState, useEffect } from 'react';
import Modal from '../common/Modal';
import { ApiError } from '../../api/client';
import { FolderIcon } from '../common/Icons';

export default function TaskFormModal({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
  projects = [],
}) {
  const isEditing = Boolean(initialData && initialData.id);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    project_id: '',
    assignee_id: '',
    status: 'TODO',
    priority: 'MEDIUM',
    due_date: '',
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || '',
        description: initialData.description || '',
        project_id: initialData.project || (initialData.project_id ? initialData.project_id : (projects[0]?.id || '')),
        assignee_id: initialData.assignee || initialData.assignee_id || '',
        status: initialData.status || 'TODO',
        priority: initialData.priority || 'MEDIUM',
        due_date: initialData.due_date || '',
      });
    } else {
      setFormData({
        title: '',
        description: '',
        project_id: projects[0]?.id || '',
        assignee_id: '',
        status: 'TODO',
        priority: 'MEDIUM',
        due_date: '',
      });
    }
    setFieldErrors({});
    setGeneralError('');
  }, [initialData, projects, isOpen]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setGeneralError('');
    setFieldErrors({});

    if (!formData.title || formData.title.trim().length < 3) {
      setFieldErrors((prev) => ({
        ...prev,
        title: ['Title must be at least 3 characters long.'],
      }));
      return;
    }

    if (!isEditing && !formData.project_id) {
      setFieldErrors((prev) => ({
        ...prev,
        project_id: ['Target project is required.'],
      }));
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        status: formData.status,
        priority: formData.priority,
        due_date: formData.due_date ? formData.due_date : null,
      };

      if (!isEditing) {
        payload.project_id = parseInt(formData.project_id, 10);
      }

      if (formData.assignee_id) {
        payload.assignee_id = parseInt(formData.assignee_id, 10);
      } else {
        payload.assignee_id = null;
      }

      await onSubmit(payload);
      onClose();
    } catch (err) {
      if (err instanceof ApiError && err.details) {
        setFieldErrors(err.details);
      }
      setGeneralError(err.message || 'Failed to save task.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? `Edit Task #${initialData.id}` : 'Create New Task'}
      maxWidth="540px"
    >
      <form onSubmit={handleSubmit} className="form">
        {generalError && <div className="alert alert-danger">{generalError}</div>}

        {/* Title */}
        <div className="form-field">
          <label htmlFor="task-title" className="label">
            Title <span className="text-danger">*</span>
          </label>
          <input
            id="task-title"
            name="title"
            type="text"
            className={`input ${fieldErrors.title ? 'is-invalid' : ''}`}
            placeholder="Task summary"
            value={formData.title}
            onChange={handleChange}
            autoFocus
          />
          {fieldErrors.title && (
            <span className="field-error">{fieldErrors.title.join(' ')}</span>
          )}
        </div>

        {/* Project */}
        {!isEditing ? (
          <div className="form-field">
            <label htmlFor="task-project" className="label">
              Project <span className="text-danger">*</span>
            </label>
            <select
              id="task-project"
              name="project_id"
              className={`select ${fieldErrors.project_id ? 'is-invalid' : ''}`}
              value={formData.project_id}
              onChange={handleChange}
            >
              <option value="">Select Project...</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            {fieldErrors.project_id && (
              <span className="field-error">{fieldErrors.project_id.join(' ')}</span>
            )}
          </div>
        ) : (
          <div className="form-field">
            <span className="label">Project</span>
            <div className="inline-meta-value">
              <FolderIcon size={14} />
              <span>{initialData.project_name || `Project #${initialData.project}`}</span>
            </div>
          </div>
        )}

        {/* Description */}
        <div className="form-field">
          <label htmlFor="task-desc" className="label">
            Description
          </label>
          <textarea
            id="task-desc"
            name="description"
            rows="3"
            className="textarea"
            placeholder="Add context, acceptance criteria..."
            value={formData.description}
            onChange={handleChange}
          ></textarea>
        </div>

        {/* Status & Priority */}
        <div className="form-grid-2">
          <div className="form-field">
            <label htmlFor="task-status" className="label">
              Status
            </label>
            <select
              id="task-status"
              name="status"
              className="select"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="TODO">To Do</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="BLOCKED">Blocked</option>
              <option value="COMPLETED">Completed</option>
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="task-priority" className="label">
              Priority
            </label>
            <select
              id="task-priority"
              name="priority"
              className="select"
              value={formData.priority}
              onChange={handleChange}
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="URGENT">Urgent</option>
            </select>
          </div>
        </div>

        {/* Assignee & Due Date */}
        <div className="form-grid-2">
          <div className="form-field">
            <label htmlFor="task-assignee" className="label">
              Assignee (User ID)
            </label>
            <input
              id="task-assignee"
              name="assignee_id"
              type="number"
              placeholder="e.g. 1"
              className={`input ${fieldErrors.assignee_id ? 'is-invalid' : ''}`}
              value={formData.assignee_id}
              onChange={handleChange}
            />
            {fieldErrors.assignee_id && (
              <span className="field-error">{fieldErrors.assignee_id.join(' ')}</span>
            )}
          </div>

          <div className="form-field">
            <label htmlFor="task-due-date" className="label">
              Due Date
            </label>
            <input
              id="task-due-date"
              name="due_date"
              type="date"
              className={`input ${fieldErrors.due_date ? 'is-invalid' : ''}`}
              value={formData.due_date}
              onChange={handleChange}
            />
            {fieldErrors.due_date && (
              <span className="field-error">{fieldErrors.due_date.join(' ')}</span>
            )}
          </div>
        </div>

        <div className="modal-actions">
          <button type="button" className="btn btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : isEditing ? 'Update Task' : 'Create Task'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
