import React from "react";
import {
  CheckSquare,
  FolderKanban,
  Plus,
  LogOut,
  LayoutGrid,
  List,
  Users,
  Search,
} from "lucide-react";

export default function Sidebar({
  user,
  projects = [],
  selectedProject,
  onSelectProject,
  onOpenCreateProject,
  onLogout,
  viewMode,
  setViewMode,
  selectedAssignee,
  setSelectedAssignee,
}) {
  const roleStyle =
    user?.role === "ADMIN"
      ? { color: "#C084FC", background: "rgba(168, 85, 247, 0.12)" }
      : user?.role === "CONTRIBUTOR"
      ? { color: "#38BDF8", background: "rgba(56, 189, 248, 0.12)" }
      : { color: "#34D399", background: "rgba(52, 211, 153, 0.12)" };

  // Team members list (Slack / Jira style)
  const teamMembers = [
    { username: "admin", name: "Admin (You)", status: "online", role: "ADMIN" },
    { username: "sarah.chen", name: "Sarah Chen", status: "online", role: "CONTRIBUTOR" },
    { username: "alex.devops", name: "Alex DevOps", status: "online", role: "CONTRIBUTOR" },
    { username: "priya.qa", name: "Priya QA", status: "offline", role: "VIEWER" },
  ];

  const getProjectColor = (index) => {
    const colors = ["#3B82F6", "#8B5CF6", "#10B981", "#F59E0B"];
    return colors[index % colors.length];
  };

  return (
    <aside className="sidebar">
      {/* Workspace Brand Header */}
      <div className="sidebar-header">
        <div className="workspace-badge">
          <div className="workspace-icon">
            <CheckSquare size={13} strokeWidth={2.5} />
          </div>
          <span style={{ fontWeight: 700 }}>TaskManager Pro</span>
        </div>
        <span
          style={{
            fontSize: "10px",
            color: "var(--text-muted)",
            background: "var(--bg-subtle)",
            padding: "2px 5px",
            borderRadius: "var(--radius-xs)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          ⌘K
        </span>
      </div>

      {/* Navigation Sections */}
      <div className="sidebar-nav">
        {/* Planning Views */}
        <div className="sidebar-section-title">Views</div>
        <div
          className={`sidebar-item ${viewMode === "board" ? "active" : ""}`}
          onClick={() => setViewMode("board")}
        >
          <LayoutGrid size={14} />
          <span>Kanban Board</span>
        </div>

        <div
          className={`sidebar-item ${viewMode === "list" ? "active" : ""}`}
          onClick={() => setViewMode("list")}
        >
          <List size={14} />
          <span>List / Spreadsheet</span>
        </div>

        {/* Projects Section */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginTop: "1.25rem",
          }}
        >
          <span className="sidebar-section-title" style={{ padding: 0 }}>
            Projects
          </span>
          {user?.role !== "VIEWER" && (
            <button
              onClick={onOpenCreateProject}
              title="Create New Project"
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "2px",
                display: "flex",
                alignItems: "center",
              }}
            >
              <Plus size={13} />
            </button>
          )}
        </div>

        {projects.length === 0 ? (
          <span style={{ fontSize: "11px", color: "var(--text-muted)", padding: "0.4rem 0.5rem" }}>
            No projects available
          </span>
        ) : (
          projects.map((proj, idx) => (
            <div
              key={proj.id}
              className={`sidebar-item ${selectedProject?.id === proj.id ? "active" : ""}`}
              onClick={() => onSelectProject(proj)}
            >
              <span
                style={{
                  width: "8px",
                  height: "8px",
                  borderRadius: "2px",
                  background: getProjectColor(idx),
                  flexShrink: 0,
                }}
              />
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {proj.name}
              </span>
            </div>
          ))
        )}

        {/* Team Members Section (Slack style) */}
        <div style={{ marginTop: "1.25rem" }}>
          <span className="sidebar-section-title" style={{ padding: 0 }}>
            Team ({teamMembers.length})
          </span>
          <div style={{ display: "flex", flexDirection: "column", gap: "2px", marginTop: "0.35rem" }}>
            {teamMembers.map((member) => (
              <div
                key={member.username}
                className={`sidebar-item ${selectedAssignee === member.username ? "active" : ""}`}
                style={{ fontSize: "12px", padding: "0.35rem 0.5rem" }}
                onClick={() =>
                  setSelectedAssignee(selectedAssignee === member.username ? null : member.username)
                }
              >
                <div style={{ position: "relative" }}>
                  <div className="issue-avatar" style={{ width: "18px", height: "18px", fontSize: "9px" }}>
                    {member.name.charAt(0)}
                  </div>
                  <span
                    style={{
                      position: "absolute",
                      bottom: "-1px",
                      right: "-1px",
                      width: "6px",
                      height: "6px",
                      borderRadius: "50%",
                      background: member.status === "online" ? "var(--status-done)" : "var(--text-muted)",
                      border: "1px solid var(--bg-sidebar)",
                    }}
                  />
                </div>
                <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {member.name}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* User Footer */}
      <div className="sidebar-footer">
        <div className="user-profile-btn">
          <div className="user-avatar-sm">
            {user?.username ? user.username.charAt(0).toUpperCase() : "U"}
          </div>
          <div style={{ display: "flex", flexDirection: "column" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-primary)" }}>
              {user?.username}
            </span>
            <span
              style={{
                fontSize: "10px",
                fontWeight: 600,
                textTransform: "uppercase",
                padding: "1px 4px",
                borderRadius: "3px",
                width: "fit-content",
                ...roleStyle,
              }}
            >
              {user?.role || "MEMBER"}
            </span>
          </div>
        </div>

        <button
          className="btn-icon"
          onClick={onLogout}
          title="Sign out"
          style={{ border: "none", padding: "0.3rem" }}
        >
          <LogOut size={15} />
        </button>
      </div>
    </aside>
  );
}
