import React, { useState } from "react";
import { X, Plus, AlertCircle } from "lucide-react";
import { createTask } from "../services/api";

export default function CreateTaskModal({
  isOpen,
  onClose,
  projects = [],
  selectedProjectId,
  onTaskCreated,
}) {
  if (!isOpen) return null;

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [projectId, setProjectId] = useState(
    selectedProjectId || (projects.length > 0 ? projects[0].id : "")
  );
  const [priority, setPriority] = useState("MEDIUM");
  const [status, setStatus] = useState("TODO");
  const [dueDate, setDueDate] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) {
      setErrorMessage("Issue title is required.");
      return;
    }
    if (!projectId) {
      setErrorMessage("Please select a project.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const payload = {
        title: title.trim(),
        description: description.trim(),
        project: parseInt(projectId, 10),
        priority,
        status,
        due_date: dueDate || null,
      };

      const newTask = await createTask(payload);
      if (onTaskCreated) onTaskCreated(newTask);
      onClose();
    } catch (err) {
      setErrorMessage(err.message || "Failed to create issue.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-dialog-header">
          <h3 className="modal-dialog-title">New Issue</h3>
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
              <label className="form-label">Project</label>
              <select
                className="form-select"
                style={{ width: "100%" }}
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                required
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Issue Title</label>
              <input
                type="text"
                className="form-input"
                placeholder="Issue summary..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                autoFocus
                required
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "0.75rem",
                marginBottom: "1rem",
              }}
            >
              <div>
                <label className="form-label">Priority</label>
                <select
                  className="form-select"
                  style={{ width: "100%" }}
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                >
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                  <option value="URGENT">Urgent</option>
                </select>
              </div>

              <div>
                <label className="form-label">Initial Status</label>
                <select
                  className="form-select"
                  style={{ width: "100%" }}
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                >
                  <option value="TODO">To Do</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="BLOCKED">Blocked</option>
                  <option value="COMPLETED">Done</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Due Date (Optional)</label>
              <input
                type="date"
                className="form-input"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-textarea"
                rows={3}
                placeholder="Add context or acceptance criteria..."
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
              <Plus size={14} />
              <span>{isSubmitting ? "Creating..." : "Create Issue"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
