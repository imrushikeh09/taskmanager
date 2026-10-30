import { apiRequest } from './client';

export const projectsApi = {
  /**
   * List projects with search, ordering, and pagination
   */
  async listProjects(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.set('search', params.search);
    if (params.ordering) query.set('ordering', params.ordering);
    if (params.page) query.set('page', params.page);
    if (params.page_size) query.set('page_size', params.page_size);

    const queryString = query.toString();
    const endpoint = queryString ? `/projects/?${queryString}` : '/projects/';
    return await apiRequest(endpoint);
  },

  /**
   * Retrieve single project details
   */
  async getProject(id) {
    return await apiRequest(`/projects/${id}/`);
  },

  /**
   * Create a new project workspace
   */
  async createProject(data) {
    return await apiRequest('/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Partially update project metadata
   */
  async updateProject(id, data) {
    return await apiRequest(`/projects/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete project and associated tasks (owner only)
   */
  async deleteProject(id) {
    return await apiRequest(`/projects/${id}/`, {
      method: 'DELETE',
    });
  },

  /**
   * Get project tasks metrics aggregated in SQL
   */
  async getProjectStats(id) {
    return await apiRequest(`/projects/${id}/stats/`);
  },

  /**
   * Get Redis cache-aside performance report
   */
  async getProjectPerformance(id) {
    return await apiRequest(`/projects/${id}/performance-report/`);
  },
};

