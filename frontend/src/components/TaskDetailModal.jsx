import React, { useState, useEffect } from "react";
import {
  X,
  Calendar,
  Paperclip,
  Upload,
  Trash2,
  Download,
  AlertCircle,
  CheckCircle2,
  Save,
  Clock,
  User,
} from "lucide-react";
import {
  updateTask,
  deleteTask,
  getAttachments,
  uploadAttachment,
  deleteAttachment,
} from "../services/api";

export default function TaskDetailModal({ task, onClose, onTaskUpdated, onTaskDeleted }) {
  if (!task) return null;

  const [title, setTitle] = useState(task.title || "");
  const [description, setDescription] = useState(task.description || "");
  const [status, setStatus] = useState(task.status || "TODO");
  const [priority, setPriority] = useState(task.priority || "MEDIUM");
  const [dueDate, setDueDate] = useState(task.due_date || "");

  const [attachments, setAttachments] = useState([]);
  const [loadingAttachments, setLoadingAttachments] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    fetchAttachments();
  }, [task.id]);

  const fetchAttachments = async () => {
    try {
      setLoadingAttachments(true);
      const data = await getAttachments(task.id);
      setAttachments(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load attachments:", err);
    } finally {
      setLoadingAttachments(false);
    }
  };

  const handleSaveChanges = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      const updated = await updateTask(task.id, {
        title,
        description,
        status,
        priority,
        due_date: dueDate || null,
      });
      setSuccessMessage("Changes saved");
      if (onTaskUpdated) onTaskUpdated(updated);
      setTimeout(() => setSuccessMessage(""), 2000);
    } catch (err) {
      setErrorMessage(err.message || "Failed to update issue.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteTask = async () => {
    if (!window.confirm(`Delete issue TM-${task.id}: "${task.title}"?`)) {
      return;
    }

    try {
      await deleteTask(task.id);
      if (onTaskDeleted) onTaskDeleted(task.id);
      onClose();
    } catch (err) {
      setErrorMessage(err.message || "Failed to delete issue.");
    }
  };

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    const file = files[0];

    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage("File exceeds 10 MB limit.");
      return;
    }

    try {
      setIsUploading(true);
      setErrorMessage("");
      await uploadAttachment(task.id, file);
      await fetchAttachments();
      setSuccessMessage("File attached");
      setTimeout(() => setSuccessMessage(""), 2000);
    } catch (err) {
      setErrorMessage(err.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteAttachment = async (attId) => {
    if (!window.confirm("Remove this attachment?")) return;
    try {
      await deleteAttachment(attId);
      setAttachments((prev) => prev.filter((a) => a.id !== attId));
    } catch (err) {
      setErrorMessage(err.message || "Failed to delete attachment.");
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  const isBug =
    task.title.toLowerCase().includes("resolve") ||
    task.title.toLowerCase().includes("saturation") ||
    task.title.toLowerCase().includes("alert");
  const isStory =
    task.title.toLowerCase().includes("mobile") ||
    task.title.toLowerCase().includes("biometric") ||
    task.title.toLowerCase().includes("offline");
  const typeClass = isBug ? "type-bug" : isStory ? "type-story" : "type-task";
  const typeLabel = isBug ? "Bug" : isStory ? "Story" : "Task";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-jira-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Jira Modal Header */}
        <div className="modal-dialog-header">
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span className={`issue-type-tag ${typeClass}`}>{typeLabel.charAt(0)}</span>
            <span style={{ fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: "13px" }}>
              TM-{task.id}
            </span>
            <span style={{ color: "var(--border-default)" }}>|</span>
            <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
              {typeLabel} Specification
            </span>
          </div>

          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Form Body: 2 Columns */}
        <form onSubmit={handleSaveChanges} style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
          <div className="modal-jira-body">
            {/* Left Column (70%): Title, Description, Acceptance Criteria, Attachments */}
            <div>
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

              {successMessage && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                    background: "rgba(48, 164, 108, 0.1)",
                    border: "1px solid rgba(48, 164, 108, 0.3)",
                    color: "#4ADE80",
                    padding: "0.5rem 0.75rem",
                    borderRadius: "var(--radius-sm)",
                    marginBottom: "1rem",
                    fontSize: "12px",
                  }}
                >
                  <CheckCircle2 size={14} />
                  <span>{successMessage}</span>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Title</label>
                <input
                  type="text"
                  className="form-input"
                  style={{ fontSize: "15px", fontWeight: 600, padding: "0.5rem 0.75rem" }}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description & Acceptance Criteria</label>
                <textarea
                  className="form-textarea"
                  rows={6}
                  placeholder="Detail user stories, architecture requirements, or reproduction steps..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              {/* Attachments Section */}
              <div style={{ marginTop: "1.5rem" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "0.5rem",
                  }}
                >
                  <label className="form-label" style={{ marginBottom: 0 }}>
                    Attachments ({attachments.length})
                  </label>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                    Max 10MB per file
                  </span>
                </div>

                <label
                  className="dropzone-box"
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    handleFileUpload(e.dataTransfer.files);
                  }}
                >
                  <Upload size={16} style={{ color: "var(--text-muted)" }} />
                  <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                    {isUploading ? "Uploading file..." : "Drop files to attach, or browse"}
                  </span>
                  <input
                    type="file"
                    style={{ display: "none" }}
                    disabled={isUploading}
                    onChange={(e) => handleFileUpload(e.target.files)}
                  />
                </label>

                <div style={{ marginTop: "0.6rem" }}>
                  {loadingAttachments ? (
                    <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                      Loading attachments...
                    </span>
                  ) : (
                    attachments.map((att) => (
                      <div key={att.id} className="attachment-row">
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "0.4rem",
                            overflow: "hidden",
                          }}
                        >
                          <Paperclip size={13} style={{ color: "var(--brand-primary)" }} />
                          <span
                            style={{
                              color: "var(--text-primary)",
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {att.file_name}
                          </span>
                          <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>
                            ({formatBytes(att.file_size_bytes)})
                          </span>
                        </div>

                        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                          <a
                            href={att.file_url}
                            download
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-icon"
                            title="Download file"
                            style={{ padding: "0.25rem" }}
                          >
                            <Download size={13} />
                          </a>
                          <button
                            type="button"
                            className="btn-icon"
                            title="Remove file"
                            style={{ padding: "0.25rem", color: "var(--priority-urgent)" }}
                            onClick={() => handleDeleteAttachment(att.id)}
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Right Column (30%): Jira Details Sidebar */}
            <div className="modal-jira-sidebar">
              <span
                style={{
                  fontSize: "11px",
                  fontWeight: 700,
                  textTransform: "uppercase",
                  letterSpacing: "0.05em",
                  color: "var(--text-muted)",
                }}
              >
                Details
              </span>

              {/* Status */}
              <div>
                <label className="form-label">Status</label>
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

              {/* Priority */}
              <div>
                <label className="form-label">Priority</label>
                <select
                  className="form-select"
                  style={{ width: "100%" }}
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                >
                  <option value="LOW">Low (▼)</option>
                  <option value="MEDIUM">Medium (■)</option>
                  <option value="HIGH">High (▲)</option>
                  <option value="URGENT">Urgent (🔴)</option>
                </select>
              </div>

              {/* Due Date */}
              <div>
                <label className="form-label">Due Date</label>
                <input
                  type="date"
                  className="form-input"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>

              {/* Assignee */}
              <div>
                <label className="form-label">Assignee</label>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 0" }}>
                  <div className="issue-avatar">
                    {task.assignee_username ? task.assignee_username.charAt(0).toUpperCase() : "—"}
                  </div>
                  <span style={{ fontSize: "12px", color: "var(--text-primary)" }}>
                    {task.assignee_username || "Unassigned"}
                  </span>
                </div>
              </div>

              <hr style={{ borderColor: "var(--border-subtle)", borderTop: "none" }} />

              {/* Metadata Timestamps */}
              <div style={{ fontSize: "11px", color: "var(--text-muted)", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                <div>Created: {task.created_at ? new Date(task.created_at).toLocaleDateString() : "Just now"}</div>
                <div>Updated: {task.updated_at ? new Date(task.updated_at).toLocaleDateString() : "Just now"}</div>
              </div>

              {/* Danger Zone */}
              <button
                type="button"
                className="btn btn-secondary"
                style={{ color: "var(--priority-urgent)", marginTop: "auto", fontSize: "12px" }}
                onClick={handleDeleteTask}
              >
                <Trash2 size={13} />
                <span>Delete Issue</span>
              </button>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="modal-dialog-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSaving}>
              <Save size={13} />
              <span>{isSaving ? "Saving..." : "Save Changes"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
