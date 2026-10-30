import { apiRequest } from './client';

export const attachmentsApi = {
  /**
   * List file attachments filtered by task ID
   */
  async listAttachments(taskId) {
    const endpoint = taskId ? `/attachments/?task=${taskId}` : '/attachments/';
    return await apiRequest(endpoint);
  },

  /**
   * Upload file attachment (multipart/form-data)
   * Max 10MB limit enforced by backend
   */
  async uploadAttachment(taskId, file) {
    const formData = new FormData();
    formData.append('task', taskId);
    formData.append('file', file);

    return await apiRequest('/attachments/', {
      method: 'POST',
      body: formData,
    });
  },

  /**
   * Delete an attachment
   */
  async deleteAttachment(id) {
    return await apiRequest(`/attachments/${id}/`, {
      method: 'DELETE',
    });
  },
};

