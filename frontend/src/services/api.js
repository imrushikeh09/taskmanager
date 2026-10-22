/**
 * Task Manager Pro - Enterprise API Client Service
 * Features: Centralized JWT management, auto token refresh, multipart upload,
 * and robust error normalization.
 */

// In modern enterprise SPAs, relative paths ('') leverage Vite dev proxy and production Nginx reverse proxy
const API_BASE_URL = "";

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

/**
 * Standard fetch wrapper with automatic JWT injection & 401 silent refresh
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = { ...options.headers };

  const token = localStorage.getItem("tm_access_token");
  if (token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Do not set Content-Type if payload is FormData (browser automatically sets boundary)
  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, { ...options, headers });

  // Handle 401 Unauthorized with automatic refresh token rotation
  if (response.status === 401 && !endpoint.includes("/auth/token/")) {
    const refreshToken = localStorage.getItem("tm_refresh_token");
    if (!refreshToken) {
      logout();
      throw new Error("Session expired. Please log in again.");
    }

    if (!isRefreshing) {
      isRefreshing = true;
      try {
        const refreshResponse = await fetch(`${API_BASE_URL}/api/v1/auth/token/refresh/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!refreshResponse.ok) {
          throw new Error("Failed to refresh session");
        }

        const data = await refreshResponse.json();
        localStorage.setItem("tm_access_token", data.access);
        isRefreshing = false;
        onRefreshed(data.access);
      } catch (err) {
        isRefreshing = false;
        logout();
        throw err;
      }
    }

    // Wait for the new token and retry the original request
    return new Promise((resolve, reject) => {
      subscribeTokenRefresh((newToken) => {
        headers["Authorization"] = `Bearer ${newToken}`;
        fetch(url, { ...options, headers })
          .then((res) => (res.status === 204 ? null : res.json()))
          .then(resolve)
          .catch(reject);
      });
    });
  }

  if (response.status === 204) {
    return null;
  }

  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch (err) {
    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}: ${response.statusText || "Service Unavailable"}`);
    }
    throw new Error("Invalid server response format.");
  }

  if (!response.ok) {
    const errorMsg =
      data.detail ||
      data.message ||
      (typeof data === "object" ? Object.values(data).flat().join(" ") : `Request failed with status ${response.status}`);
    throw new Error(errorMsg);
  }

  return data;
}

// -----------------------------------------------------------------------------
// Authentication Endpoints
// -----------------------------------------------------------------------------
export async function login(username, password) {
  const data = await request("/api/v1/auth/token/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
  localStorage.setItem("tm_access_token", data.access);
  localStorage.setItem("tm_refresh_token", data.refresh);
  return data;
}

export async function getCurrentUser() {
  return request("/api/v1/auth/me/");
}

export function logout() {
  localStorage.removeItem("tm_access_token");
  localStorage.removeItem("tm_refresh_token");
  window.dispatchEvent(new Event("auth_logout"));
}

export function isAuthenticated() {
  return !!localStorage.getItem("tm_access_token");
}

// -----------------------------------------------------------------------------
// Projects Endpoints
// -----------------------------------------------------------------------------
export async function getProjects() {
  const data = await request("/api/v1/projects/");
  return data.results || data;
}

export async function createProject(projectData) {
  return request("/api/v1/projects/", {
    method: "POST",
    body: JSON.stringify(projectData),
  });
}

export async function getProjectStats(projectId) {
  return request(`/api/v1/projects/${projectId}/stats/`);
}

// -----------------------------------------------------------------------------
// Tasks Endpoints
// -----------------------------------------------------------------------------
export async function getTasks(projectId = null) {
  let url = "/api/v1/tasks/?ordering=-created_at";
  if (projectId) {
    url += `&project=${projectId}`;
  }
  const data = await request(url);
  return data.results || data;
}

export async function createTask(taskData) {
  return request("/api/v1/tasks/", {
    method: "POST",
    body: JSON.stringify(taskData),
  });
}

export async function updateTask(taskId, updates) {
  return request(`/api/v1/tasks/${taskId}/`, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}

export async function deleteTask(taskId) {
  return request(`/api/v1/tasks/${taskId}/`, {
    method: "DELETE",
  });
}

// -----------------------------------------------------------------------------
// Attachments Endpoints
// -----------------------------------------------------------------------------
export async function getAttachments(taskId) {
  const data = await request(`/api/v1/attachments/?task=${taskId}`);
  return data.results || data;
}

export async function uploadAttachment(taskId, file) {
  const formData = new FormData();
  formData.append("task", taskId);
  formData.append("file", file);

  return request("/api/v1/attachments/", {
    method: "POST",
    body: formData,
  });
}

export async function deleteAttachment(attachmentId) {
  return request(`/api/v1/attachments/${attachmentId}/`, {
    method: "DELETE",
  });
}

// -----------------------------------------------------------------------------
// Notifications Endpoints
// -----------------------------------------------------------------------------
export async function getNotifications(isRead = null) {
  let url = "/api/v1/notifications/";
  if (isRead !== null) {
    url += `?is_read=${isRead}`;
  }
  const data = await request(url);
  return data.results || data;
}

export async function markNotificationAsRead(id) {
  return request(`/api/v1/notifications/${id}/read/`, {
    method: "POST",
  });
}

export async function markAllNotificationsAsRead() {
  return request("/api/v1/notifications/read-all/", {
    method: "POST",
  });
}
