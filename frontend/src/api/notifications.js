import { apiRequest } from './client';

export const notificationsApi = {
  /**
   * List in-app notifications for authenticated user
   * @param {Object} params - { is_read: boolean, page: number }
   */
  async listNotifications(params = {}) {
    const query = new URLSearchParams();
    if (params.is_read !== undefined && params.is_read !== null) {
      query.set('is_read', params.is_read);
    }
    if (params.page) query.set('page', params.page);

    const queryString = query.toString();
    const endpoint = queryString ? `/notifications/?${queryString}` : '/notifications/';
    return await apiRequest(endpoint);
  },

  /**
   * Mark a single notification as read
   */
  async markAsRead(id) {
    return await apiRequest(`/notifications/${id}/read/`, {
      method: 'POST',
    });
  },

  /**
   * Mark all unread notifications as read for current user
   */
  async markAllAsRead() {
    return await apiRequest('/notifications/read-all/', {
      method: 'POST',
    });
  },
};

