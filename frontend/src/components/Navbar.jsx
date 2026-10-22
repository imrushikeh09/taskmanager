import React from "react";
import { Plus, Bell, LayoutGrid, List, Search, Filter, AlertTriangle, UserCheck } from "lucide-react";

export default function Navbar({
  selectedProject,
  unreadCount,
  onOpenNotifications,
  onOpenCreateTask,
  user,
  viewMode,
  setViewMode,
  quickFilter,
  setQuickFilter,
  searchQuery,
  setSearchQuery,
}) {
  return (
    <div>
      {/* Top Header Command Bar */}
      <header className="top-header">
        {/* Breadcrumb Path */}
        <div className="breadcrumbs">
          <span style={{ color: "var(--text-muted)" }}>Projects</span>
          <span style={{ color: "var(--border-default)" }}>/</span>
          <span className="breadcrumb-active">
            {selectedProject ? selectedProject.name : "Select Project"}
          </span>
        </div>

        {/* View Toggle & Actions */}
        <div className="header-actions">
          {/* Dual View Toggle (Board vs List) */}
          <div className="view-toggle-group">
            <button
              className={`view-toggle-btn ${viewMode === "board" ? "active" : ""}`}
              onClick={() => setViewMode("board")}
              title="Kanban Board View"
            >
              <LayoutGrid size={13} />
              <span>Board</span>
            </button>
            <button
              className={`view-toggle-btn ${viewMode === "list" ? "active" : ""}`}
              onClick={() => setViewMode("list")}
              title="List / Spreadsheet View"
            >
              <List size={13} />
              <span>List</span>
            </button>
          </div>

          {/* Notifications Bell */}
          <button
            className="btn-icon"
            onClick={onOpenNotifications}
            title="In-app notification alerts"
          >
            <Bell size={15} />
            {unreadCount > 0 && (
              <span
                style={{
                  position: "absolute",
                  top: "-3px",
                  right: "-3px",
                  width: "14px",
                  height: "14px",
                  borderRadius: "var(--radius-full)",
                  background: "var(--priority-urgent)",
                  color: "white",
                  fontSize: "9px",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {unreadCount > 9 ? "9+" : unreadCount}
              </span>
            )}
          </button>

          {/* Create Issue Action */}
          {user?.role !== "VIEWER" && (
            <button className="btn btn-primary" onClick={onOpenCreateTask}>
              <Plus size={14} />
              <span>Create Issue</span>
            </button>
          )}
        </div>
      </header>

      {/* Azure Boards / Jira Quick Filter Strip */}
      <div className="quick-filter-strip">
        <div className="filter-chip-group">
          {/* Search Input */}
          <div className="search-input-wrapper" style={{ width: "220px" }}>
            <Search size={13} className="search-icon" />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: "1.75rem", fontSize: "12px", padding: "0.25rem 0.5rem 0.25rem 1.75rem" }}
              placeholder="Search issues (title, desc)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div
            className={`filter-chip ${quickFilter === "ALL" ? "active" : ""}`}
            onClick={() => setQuickFilter("ALL")}
          >
            <span>All Issues</span>
          </div>

          <div
            className={`filter-chip ${quickFilter === "MY_ISSUES" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "MY_ISSUES" ? "ALL" : "MY_ISSUES")}
          >
            <UserCheck size={12} />
            <span>Only My Issues</span>
          </div>

          <div
            className={`filter-chip ${quickFilter === "URGENT_HIGH" ? "active" : ""}`}
            onClick={() => setQuickFilter(quickFilter === "URGENT_HIGH" ? "ALL" : "URGENT_HIGH")}
          >
            <AlertTriangle size={12} style={{ color: "var(--priority-urgent)" }} />
            <span>Urgent & High</span>
          </div>
        </div>
      </div>
    </div>
  );
}
