import React, { useState, useEffect } from 'react';
import Modal from '../common/Modal';
import { ApiError } from '../../api/client';

export default function ProjectFormModal({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
}) {
  const isEditing = Boolean(initialData && initialData.id);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
  });

  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
      });
    } else {
      setFormData({
        name: '',
        description: '',
      });
    }
    setFieldErrors({});
    setGeneralError('');
  }, [initialData, isOpen]);

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

    if (!formData.name.trim()) {
      setFieldErrors({ name: ['Project name is required.'] });
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        name: formData.name.trim(),
        description: formData.description.trim(),
      });
      onClose();
    } catch (err) {
      if (err instanceof ApiError && err.details) {
        setFieldErrors(err.details);
      }
      setGeneralError(err.message || 'Failed to save project.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? `Edit Project: ${initialData.name}` : 'Create New Project'}
      maxWidth="500px"
    >
      <form onSubmit={handleSubmit} className="project-form">
        {generalError && <div className="form-alert error">{generalError}</div>}

        <div className="form-group">
          <label htmlFor="proj-name" className="form-label">
            Project Name <span className="required-star">*</span>
          </label>
          <input
            id="proj-name"
            name="name"
            type="text"
            className={`form-input ${fieldErrors.name ? 'has-error' : ''}`}
            placeholder="e.g. Core Cloud Infrastructure"
            value={formData.name}
            onChange={handleChange}
            autoFocus
          />
          {fieldErrors.name && (
            <span className="form-error-msg">{fieldErrors.name.join(' ')}</span>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="proj-desc" className="form-label">
            Description
          </label>
          <textarea
            id="proj-desc"
            name="description"
            rows="3"
            className="form-textarea"
            placeholder="High-level project scope, roadmap, or purpose..."
            value={formData.description}
            onChange={handleChange}
          ></textarea>
        </div>

        <div className="modal-actions-bar">
          <button type="button" className="btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : isEditing ? 'Update Project' : 'Create Project'}
          </button>
        </div>
      </form>
    </Modal>
  );
}

