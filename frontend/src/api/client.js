/**
 * API Client with JWT Bearer Token Injection & Automatic Refresh
 * Complies with Task Manager API Contract v1 (docs/api_contract.md)
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const TOKEN_KEYS = {
  ACCESS: 'tm_access_token',
  REFRESH: 'tm_refresh_token',
  USER: 'tm_current_user',
};

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEYS.ACCESS);
}

export function getRefreshToken() {
  return localStorage.getItem(TOKEN_KEYS.REFRESH);
}

export function setTokens(access, refresh) {
  if (access) localStorage.setItem(TOKEN_KEYS.ACCESS, access);
  if (refresh) localStorage.setItem(TOKEN_KEYS.REFRESH, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEYS.ACCESS);
  localStorage.removeItem(TOKEN_KEYS.REFRESH);
  localStorage.removeItem(TOKEN_KEYS.USER);
}

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

/**
 * Core HTTP Request Wrapper
 */
export async function apiRequest(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  const headers = new Headers(options.headers || {});

  // Add auth header if token exists and not already provided
  const token = getAccessToken();
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  // Set default JSON Content-Type unless payload is FormData
  const isFormData = options.body instanceof FormData;
  if (!isFormData && !headers.has('Content-Type') && options.method && options.method !== 'GET') {
    headers.set('Content-Type', 'application/json');
  }

  const config = {
    ...options,
    headers,
  };

  try {
    let response = await fetch(url, config);

    // Handle 401 Unauthorized with token refresh mechanism
    if (response.status === 401 && !options._retry && getRefreshToken()) {
      if (isRefreshing) {
        // Queue pending requests while token refresh completes
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((newToken) => {
            config.headers.set('Authorization', `Bearer ${newToken}`);
            return fetch(url, config).then(handleResponse);
          })
          .catch((err) => Promise.reject(err));
      }

      options._retry = true;
      isRefreshing = true;

      try {
        const refreshResponse = await fetch(`${BASE_URL}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: getRefreshToken() }),
        });

        if (refreshResponse.ok) {
          const refreshData = await refreshResponse.json();
          setTokens(refreshData.access);
          processQueue(null, refreshData.access);

          config.headers.set('Authorization', `Bearer ${refreshData.access}`);
          return fetch(url, config).then(handleResponse);
        } else {
          // Refresh token invalid or expired
          clearTokens();
          processQueue(new Error('Session expired'), null);
          window.dispatchEvent(new CustomEvent('auth:expired'));
          throw new ApiError('Session expired. Please log in again.', 401, 'AUTHENTICATION_FAILED');
        }
      } catch (refreshErr) {
        clearTokens();
        processQueue(refreshErr, null);
        window.dispatchEvent(new CustomEvent('auth:expired'));
        throw refreshErr;
      } finally {
        isRefreshing = false;
      }
    }

    return await handleResponse(response);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    // Network or parse error
    throw new ApiError(error.message || 'Network request failed', 0, 'NETWORK_ERROR');
  }
}

/**
 * Handle HTTP response and standardize API envelope parsing
 */
async function handleResponse(response) {
  // 204 No Content
  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  let payload = null;
  if (contentType.includes('application/json')) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    // Check for standardized API Contract envelope
    // { error: { code, message, details } }
    if (payload && payload.error) {
      throw new ApiError(
        payload.error.message || 'An error occurred',
        response.status,
        payload.error.code || 'UNKNOWN_ERROR',
        payload.error.details || {}
      );
    }

    // Standard DRF detail format or fallback
    const detailMsg =
      typeof payload === 'object' && payload !== null
        ? payload.detail || payload.message || JSON.stringify(payload)
        : payload;

    throw new ApiError(detailMsg || `Request failed with status ${response.status}`, response.status);
  }

  return payload;
}

/**
 * Custom Error Class for Structured Error Handling
 */
export class ApiError extends Error {
  constructor(message, status = 500, code = 'INTERNAL_ERROR', details = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

