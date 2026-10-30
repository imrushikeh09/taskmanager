import { apiRequest, setTokens, clearTokens } from './client';

export const authApi = {
  /**
   * Authenticate user credentials and store JWT tokens
   * @param {string} username
   * @param {string} password
   */
  async login(username, password) {
    const data = await apiRequest('/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });

    if (data && data.access) {
      setTokens(data.access, data.refresh);
    }
    return data;
  },

  /**
   * Retrieve active user profile and RBAC role
   */
  async getCurrentUser() {
    return await apiRequest('/auth/me/');
  },

  /**
   * Log out active session
   */
  logout() {
    clearTokens();
  },
};

