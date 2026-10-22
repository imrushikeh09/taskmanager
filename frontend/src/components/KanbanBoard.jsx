import React, { useState } from "react";
import TaskCard from "./TaskCard";
import { Plus, Search, Filter, Layers } from "lucide-react";

const COLUMNS = [
  { key: "TODO", title: "To Do", dotClass: "dot-todo" },
  { key: "IN_PROGRESS", title: "In Progress", dotClass: "dot-progress" },
  { key: "BLOCKED", title: "Blocked", dotClass: "dot-blocked" },
  { key: "COMPLETED", title: "Done", dotClass: "dot-done" },
];

export default function KanbanBoard({
  tasks = [],
  onTaskClick,
  onStatusChange,
  onCreateTaskClick,
  searchQuery,
  setSearchQuery,
  priorityFilter,
  setPriorityFilter,
}) {
  const [draggedTaskId, setDraggedTaskId] = useState(null);

  const filteredTasks = tasks.filter((t) => {
    const matchesSearch =
      !searchQuery ||
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (t.description && t.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesPriority =
      !priorityFilter || priorityFilter === "ALL" || t.priority === priorityFilter;

    return matchesSearch && matchesPriority;
  });

  const handleDragStart = (e, taskId) => {
    setDraggedTaskId(taskId);
    e.dataTransfer.setData("text/plain", taskId.toString());
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  };

  const handleDrop = (e, targetStatus) => {
    e.preventDefault();
    const taskId = draggedTaskId || e.dataTransfer.getData("text/plain");
    if (taskId && onStatusChange) {
      onStatusChange(parseInt(taskId, 10), targetStatus);
    }
    setDraggedTaskId(null);
  };

  return (
    <div className="kanban-view">
      {/* Board Controls */}
      <div className="kanban-controls">
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {/* Search */}
          <div className="search-input-wrapper">
            <Search size={14} className="search-icon" />
            <input
              type="text"
              className="form-input"
              style={{ paddingLeft: "1.85rem" }}
              placeholder="Filter issues..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Priority Filter */}
          <select
            className="form-select"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="ALL">All Priorities</option>
            <option value="URGENT">Urgent</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <button className="btn btn-secondary" onClick={onCreateTaskClick}>
          <Plus size={14} />
          <span>New Issue</span>
        </button>
      </div>

      {/* Kanban Grid */}
      <div className="kanban-grid">
        {COLUMNS.map((col) => {
          const colTasks = filteredTasks.filter((t) => t.status === col.key);

          return (
            <div
              key={col.key}
              className="kanban-column"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, col.key)}
            >
              <div className="column-header">
                <div className="column-title-group">
                  <span className={`column-dot ${col.dotClass}`} />
                  <span>{col.title}</span>
                </div>
                <span className="column-count">{colTasks.length}</span>
              </div>

              <div className="column-cards">
                {colTasks.length === 0 ? (
                  <div
                    style={{
                      border: "1px dashed var(--border-subtle)",
                      borderRadius: "var(--radius-sm)",
                      padding: "1.5rem 1rem",
                      textAlign: "center",
                      color: "var(--text-muted)",
                      fontSize: "12px",
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: "0.25rem",
                    }}
                  >
                    <span>No issues</span>
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <div
                      key={task.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, task.id)}
                      style={{ cursor: "grab" }}
                    >
                      <TaskCard task={task} onClick={onTaskClick} />
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
