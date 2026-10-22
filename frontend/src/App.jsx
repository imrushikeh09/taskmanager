import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import ProjectStats from "./components/ProjectStats";
import KanbanBoard from "./components/KanbanBoard";
import ListView from "./components/ListView";
import LoginModal from "./components/LoginModal";
import TaskDetailModal from "./components/TaskDetailModal";
import CreateTaskModal from "./components/CreateTaskModal";
import CreateProjectModal from "./components/CreateProjectModal";
import NotificationDrawer from "./components/NotificationDrawer";
import {
  isAuthenticated,
  getCurrentUser,
  getProjects,
  getTasks,
  updateTask,
  getNotifications,
  logout,
} from "./services/api";
import { FolderPlus, Loader2 } from "lucide-react";

export default function App() {
  const [authed, setAuthed] = useState(isAuthenticated());
  const [currentUser, setCurrentUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  // View modes & filters (Jira / Azure Boards)
  const [viewMode, setViewMode] = useState("board"); // "board" | "list"
  const [quickFilter, setQuickFilter] = useState("ALL"); // "ALL" | "MY_ISSUES" | "URGENT_HIGH"
  const [selectedAssignee, setSelectedAssignee] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("ALL");

  // Modals & Panels
  const [selectedTask, setSelectedTask] = useState(null);
  const [isCreateTaskOpen, setIsCreateTaskOpen] = useState(false);
  const [isCreateProjectOpen, setIsCreateProjectOpen] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);

  useEffect(() => {
    const handleAuthLogout = () => {
      setAuthed(false);
      setCurrentUser(null);
      setProjects([]);
      setSelectedProject(null);
      setTasks([]);
      setNotifications([]);
    };

    window.addEventListener("auth_logout", handleAuthLogout);
    return () => window.removeEventListener("auth_logout", handleAuthLogout);
  }, []);

  useEffect(() => {
    if (authed) {
      loadWorkspaceData();
    } else {
      setLoading(false);
    }
  }, [authed]);

  const loadWorkspaceData = async () => {
    try {
      setLoading(true);
      const user = await getCurrentUser();
      setCurrentUser(user);

      const projs = await getProjects();
      setProjects(projs);

      if (projs.length > 0) {
        const activeProj = projs[0];
        setSelectedProject(activeProj);
        const projectTasks = await getTasks(activeProj.id);
        setTasks(projectTasks);
      } else {
        setTasks([]);
      }

      const notifs = await getNotifications();
      setNotifications(Array.isArray(notifs) ? notifs : []);
    } catch (err) {
      console.error("Workspace load error:", err);
      if (err.message.includes("Session expired") || err.message.includes("401")) {
        setAuthed(false);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectProject = async (project) => {
    setSelectedProject(project);
    try {
      setLoading(true);
      const projectTasks = await getTasks(project.id);
      setTasks(projectTasks);
    } catch (err) {
      console.error("Failed to load project tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
    );

    try {
      const updated = await updateTask(taskId, { status: newStatus });
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
      refreshNotifications();
    } catch (err) {
      console.error("Failed to update status:", err);
      if (selectedProject) {
        const freshTasks = await getTasks(selectedProject.id);
        setTasks(freshTasks);
      }
    }
  };

  const handleTaskCreated = (newTask) => {
    setTasks((prev) => [newTask, ...prev]);
    refreshNotifications();
  };

  const handleTaskUpdated = (updatedTask) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
    setSelectedTask(updatedTask);
    refreshNotifications();
  };

  const handleTaskDeleted = (deletedTaskId) => {
    setTasks((prev) => prev.filter((t) => t.id !== deletedTaskId));
    setSelectedTask(null);
  };

  const handleProjectCreated = async (newProj) => {
    setProjects((prev) => [...prev, newProj]);
    setSelectedProject(newProj);
    setTasks([]);
  };

  const refreshNotifications = async () => {
    try {
      const notifs = await getNotifications();
      setNotifications(Array.isArray(notifs) ? notifs : []);
    } catch (err) {
      console.error("Failed to refresh notifications:", err);
    }
  };

  const handleLogout = () => {
    logout();
    setAuthed(false);
    setCurrentUser(null);
  };

  if (!authed) {
    return <LoginModal onLoginSuccess={() => setAuthed(true)} />;
  }

  const unreadNotifCount = notifications.filter((n) => !n.is_read).length;

  // Filter tasks through Quick Filters + Assignee + Search
  const filteredTasks = tasks.filter((task) => {
    // 1. Assignee sidebar filter
    if (selectedAssignee && task.assignee_username !== selectedAssignee) {
      return false;
    }

    // 2. Quick filter strip
    if (quickFilter === "MY_ISSUES" && task.assignee_username !== currentUser?.username) {
      return false;
    }
    if (quickFilter === "URGENT_HIGH" && task.priority !== "URGENT" && task.priority !== "HIGH") {
      return false;
    }

    // 3. Search query
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchTitle = task.title.toLowerCase().includes(q);
      const matchDesc = task.description && task.description.toLowerCase().includes(q);
      const matchKey = `tm-${task.id}`.includes(q);
      if (!matchTitle && !matchDesc && !matchKey) return false;
    }

    // 4. Priority filter
    if (priorityFilter !== "ALL" && task.priority !== priorityFilter) {
      return false;
    }

    return true;
  });

  return (
    <div className="app-shell">
      {/* Slack & Jira Collapsible Sidebar */}
      <Sidebar
        user={currentUser}
        projects={projects}
        selectedProject={selectedProject}
        onSelectProject={handleSelectProject}
        onOpenCreateProject={() => setIsCreateProjectOpen(true)}
        onLogout={handleLogout}
        viewMode={viewMode}
        setViewMode={setViewMode}
        selectedAssignee={selectedAssignee}
        setSelectedAssignee={setSelectedAssignee}
      />

      {/* Main Workspace Area */}
      <div className="workspace-main">
        {/* Top Command Bar & Azure Quick Filter Strip */}
        <Navbar
          selectedProject={selectedProject}
          unreadCount={unreadNotifCount}
          onOpenNotifications={() => setIsNotificationOpen(true)}
          onOpenCreateTask={() => setIsCreateTaskOpen(true)}
          user={currentUser}
          viewMode={viewMode}
          setViewMode={setViewMode}
          quickFilter={quickFilter}
          setQuickFilter={setQuickFilter}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />

        {loading ? (
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.5rem",
              color: "var(--text-muted)",
              fontSize: "13px",
            }}
          >
            <Loader2 size={16} className="animate-spin" />
            <span>Loading enterprise workspace...</span>
          </div>
        ) : projects.length === 0 ? (
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: "2rem",
              textAlign: "center",
            }}
          >
            <FolderPlus size={36} style={{ color: "var(--text-muted)", marginBottom: "0.75rem" }} />
            <h3 style={{ fontSize: "15px", marginBottom: "0.25rem", color: "var(--text-primary)" }}>
              No projects created
            </h3>
            <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "1rem" }}>
              Create your first project to start tracking enterprise issues and sprints.
            </p>
            <button className="btn btn-primary" onClick={() => setIsCreateProjectOpen(true)}>
              <FolderPlus size={14} />
              <span>Create Project</span>
            </button>
          </div>
        ) : (
          <>
            {/* Real-Time Metrics Strip */}
            <ProjectStats tasks={filteredTasks} />

            {/* Dual Views: Kanban Board OR High-Density Table */}
            {viewMode === "board" ? (
              <KanbanBoard
                tasks={filteredTasks}
                onTaskClick={(task) => setSelectedTask(task)}
                onStatusChange={handleStatusChange}
                onCreateTaskClick={() => setIsCreateTaskOpen(true)}
                searchQuery=""
                setSearchQuery={() => {}}
                priorityFilter="ALL"
                setPriorityFilter={() => {}}
              />
            ) : (
              <ListView
                tasks={filteredTasks}
                onTaskClick={(task) => setSelectedTask(task)}
              />
            )}
          </>
        )}
      </div>

      {/* Two-Column Jira Issue Inspector Modal */}
      {selectedTask && (
        <TaskDetailModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
          onTaskUpdated={handleTaskUpdated}
          onTaskDeleted={handleTaskDeleted}
        />
      )}

      {isCreateTaskOpen && (
        <CreateTaskModal
          isOpen={isCreateTaskOpen}
          onClose={() => setIsCreateTaskOpen(false)}
          projects={projects}
          selectedProjectId={selectedProject?.id}
          onTaskCreated={handleTaskCreated}
        />
      )}

      {isCreateProjectOpen && (
        <CreateProjectModal
          isOpen={isCreateProjectOpen}
          onClose={() => setIsCreateProjectOpen(false)}
          onProjectCreated={handleProjectCreated}
        />
      )}

      <NotificationDrawer
        isOpen={isNotificationOpen}
        onClose={() => setIsNotificationOpen(false)}
        notifications={notifications}
        onRefreshNotifications={refreshNotifications}
      />
    </div>
  );
}
