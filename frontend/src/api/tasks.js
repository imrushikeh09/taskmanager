import { apiRequest } from './client';

export const tasksApi = {
  /**
   * List tasks with multi-field filtering, search, ordering, and pagination
   */
  async listTasks(params = {}) {
    const query = new URLSearchParams();
    if (params.project) query.set('project', params.project);
    if (params.status) query.set('status', params.status);
    if (params.priority) query.set('priority', params.priority);
    if (params.assignee) query.set('assignee', params.assignee);
    if (params.due_date_before) query.set('due_date_before', params.due_date_before);
    if (params.search) query.set('search', params.search);
    if (params.ordering) query.set('ordering', params.ordering);
    if (params.page) query.set('page', params.page);
    if (params.page_size) query.set('page_size', params.page_size);

    const queryString = query.toString();
    const endpoint = queryString ? `/tasks/?${queryString}` : '/tasks/';
    return await apiRequest(endpoint);
  },

  /**
   * Retrieve task details with populated relationships
   */
  async getTask(id) {
    return await apiRequest(`/tasks/${id}/`);
  },

  /**
   * Create a new task linked to project and assignee
   */
  async createTask(data) {
    return await apiRequest('/tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Partially update task attributes (status, priority, assignee, due_date, title, description)
   */
  async updateTask(id, data) {
    return await apiRequest(`/tasks/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete task
   */
  async deleteTask(id) {
    return await apiRequest(`/tasks/${id}/`, {
      method: 'DELETE',
    });
  },
};

