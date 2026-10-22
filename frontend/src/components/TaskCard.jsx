import React from "react";
import { Calendar, Paperclip, AlertCircle } from "lucide-react";

export default function TaskCard({ task, onClick }) {
  const overdue =
    task.due_date &&
    task.status !== "COMPLETED" &&
    task.due_date < new Date().toISOString().split("T")[0];

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case "URGENT":
        return <span className="priority-badge priority-urgent">🔴 Urgent</span>;
      case "HIGH":
        return <span className="priority-badge priority-high">▲ High</span>;
      case "MEDIUM":
        return <span className="priority-badge priority-medium">■ Med</span>;
      default:
        return <span className="priority-badge priority-low">▼ Low</span>;
    }
  };

  // Issue type inference (Task / Story / Bug)
  const isBug =
    task.title.toLowerCase().includes("resolve") ||
    task.title.toLowerCase().includes("saturation") ||
    task.title.toLowerCase().includes("alert");
  const isStory =
    task.title.toLowerCase().includes("mobile") ||
    task.title.toLowerCase().includes("biometric") ||
    task.title.toLowerCase().includes("offline");
  const typeClass = isBug ? "type-bug" : isStory ? "type-story" : "type-task";
  const typeLetter = isBug ? "B" : isStory ? "S" : "T";

  const assigneeInitial = task.assignee_username
    ? task.assignee_username.charAt(0).toUpperCase()
    : "—";

  return (
    <div className="issue-card" onClick={() => onClick(task)}>
      {/* Top Header: Issue Type, Key, Priority */}
      <div className="issue-card-header">
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <span className={`issue-type-tag ${typeClass}`} title={isBug ? "Bug" : isStory ? "Story" : "Task"}>
            {typeLetter}
          </span>
          <span className="issue-identifier">TM-{task.id}</span>
        </div>
        {getPriorityBadge(task.priority)}
      </div>

      {/* Title */}
      <div className="issue-title">{task.title}</div>

      {/* Description Preview */}
      {task.description && (
        <div className="issue-desc">{task.description}</div>
      )}

      {/* Card Footer */}
      <div className="issue-footer">
        <div className="issue-meta-items">
          {task.due_date && (
            overdue ? (
              <span className="badge-overdue" title="Overdue task!">
                <AlertCircle size={9} />
                {task.due_date}
              </span>
            ) : (
              <div className="issue-meta-item" title={`Due: ${task.due_date}`}>
                <Calendar size={11} />
                <span>{task.due_date}</span>
              </div>
            )
          )}

          <div className="issue-meta-item" title="Attachments">
            <Paperclip size={11} />
            <span>Files</span>
          </div>
        </div>

        <div
          className="issue-avatar"
          title={`Assigned to: ${task.assignee_username || "Unassigned"}`}
        >
          {assigneeInitial}
        </div>
      </div>
    </div>
  );
}
