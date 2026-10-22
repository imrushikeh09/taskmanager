import React, { useState } from "react";
import { X, FolderPlus, AlertCircle } from "lucide-react";
import { createProject } from "../services/api";

export default function CreateProjectModal({ isOpen, onClose, onProjectCreated }) {
  if (!isOpen) return null;

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setErrorMessage("Project name is required.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const newProject = await createProject({
        name: name.trim(),
        description: description.trim(),
      });
      if (onProjectCreated) onProjectCreated(newProject);
      setName("");
      setDescription("");
      onClose();
    } catch (err) {
      setErrorMessage(err.message || "Failed to create project.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-dialog-header">
          <h3 className="modal-dialog-title">New Project</h3>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-dialog-body">
            {errorMessage && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.5rem",
                  background: "rgba(229, 72, 77, 0.1)",
                  border: "1px solid rgba(229, 72, 77, 0.3)",
                  color: "#F87171",
                  padding: "0.5rem 0.75rem",
                  borderRadius: "var(--radius-sm)",
                  marginBottom: "1rem",
                  fontSize: "12px",
                }}
              >
                <AlertCircle size={14} />
                <span>{errorMessage}</span>
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Project Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Core Infrastructure"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoFocus
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description (Optional)</label>
              <textarea
                className="form-textarea"
                rows={3}
                placeholder="Project scope and goals..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-dialog-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              <FolderPlus size={14} />
              <span>{isSubmitting ? "Creating..." : "Create Project"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
