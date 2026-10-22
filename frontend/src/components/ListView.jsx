import React from "react";
import { AlertCircle, Calendar, Paperclip, CheckCircle2 } from "lucide-react";

export default function ListView({ tasks = [], onTaskClick }) {
  const isOverdue = (dueDate, status) => {
    if (!dueDate || status === "COMPLETED") return false;
    const today = new Date().toISOString().split("T")[0];
    return dueDate < today;
  };

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

  const getStatusBadge = (status) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span style={{ color: "var(--status-done)", display: "flex", alignItems: "center", gap: "4px" }}>
            <span className="column-dot dot-done" /> Done
          </span>
        );
      case "IN_PROGRESS":
        return (
          <span style={{ color: "var(--status-progress)", display: "flex", alignItems: "center", gap: "4px" }}>
            <span className="column-dot dot-progress" /> In Progress
          </span>
        );
      case "BLOCKED":
        return (
          <span style={{ color: "var(--status-blocked)", display: "flex", alignItems: "center", gap: "4px" }}>
            <span className="column-dot dot-blocked" /> Blocked
          </span>
        );
      default:
        return (
          <span style={{ color: "var(--status-todo)", display: "flex", alignItems: "center", gap: "4px" }}>
            <span className="column-dot dot-todo" /> To Do
          </span>
        );
    }
  };

  return (
    <div className="table-view-container">
      <table className="jira-table">
        <thead>
          <tr>
            <th style={{ width: "45px" }}>Type</th>
            <th style={{ width: "80px" }}>Key</th>
            <th>Title</th>
            <th style={{ width: "130px" }}>Status</th>
            <th style={{ width: "110px" }}>Priority</th>
            <th style={{ width: "150px" }}>Assignee</th>
            <th style={{ width: "130px" }}>Due Date</th>
            <th style={{ width: "70px", textAlign: "center" }}>Files</th>
          </tr>
        </thead>
        <tbody>
          {tasks.length === 0 ? (
            <tr>
              <td colSpan={8} style={{ textAlign: "center", padding: "2.5rem", color: "var(--text-muted)" }}>
                No issues match your current filters.
              </td>
            </tr>
          ) : (
            tasks.map((task) => {
              const overdue = isOverdue(task.due_date, task.status);
              const assigneeInitial = task.assignee_username
                ? task.assignee_username.charAt(0).toUpperCase()
                : "—";

              // Infer issue type
              const isBug = task.title.toLowerCase().includes("resolve") || task.title.toLowerCase().includes("saturation");
              const isStory = task.title.toLowerCase().includes("mobile") || task.title.toLowerCase().includes("biometric") || task.title.toLowerCase().includes("offline");
              const typeClass = isBug ? "type-bug" : isStory ? "type-story" : "type-task";
              const typeLetter = isBug ? "B" : isStory ? "S" : "T";

              return (
                <tr key={task.id} onClick={() => onTaskClick(task)}>
                  <td>
                    <span className={`issue-type-tag ${typeClass}`} title={isBug ? "Bug / Incident" : isStory ? "User Story" : "Task"}>
                      {typeLetter}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontFamily: "var(--font-mono)", fontWeight: 600, color: "var(--text-muted)" }}>
                      TM-{task.id}
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 500, color: "var(--text-primary)" }}>
                      {task.title}
                    </span>
                  </td>
                  <td>{getStatusBadge(task.status)}</td>
                  <td>{getPriorityBadge(task.priority)}</td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                      <div className="issue-avatar">{assigneeInitial}</div>
                      <span style={{ color: "var(--text-secondary)" }}>
                        {task.assignee_username || "Unassigned"}
                      </span>
                    </div>
                  </td>
                  <td>
                    {task.due_date ? (
                      overdue ? (
                        <span className="badge-overdue" title="Overdue task!">
                          <AlertCircle size={10} />
                          {task.due_date}
                        </span>
                      ) : (
                        <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>
                          {task.due_date}
                        </span>
                      )
                    ) : (
                      <span style={{ color: "var(--text-muted)" }}>—</span>
                    )}
                  </td>
                  <td style={{ textAlign: "center", color: "var(--text-muted)" }}>
                    <Paperclip size={12} />
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
