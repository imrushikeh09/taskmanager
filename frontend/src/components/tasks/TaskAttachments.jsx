import React, { useState, useEffect, useCallback } from 'react';
import { attachmentsApi } from '../../api/attachments';
import LoadingSpinner from '../common/LoadingSpinner';
import { PaperclipIcon, UploadCloudIcon, DownloadIcon, TrashIcon } from '../common/Icons';

const MAX_BYTES = 10 * 1024 * 1024; // 10MB limit

function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function TaskAttachments({ taskId, canEdit = true }) {
  const [attachments, setAttachments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const fetchAttachments = useCallback(async () => {
    if (!taskId) return;
    try {
      setIsLoading(true);
      const data = await attachmentsApi.listAttachments(taskId);
      const list = data.results || (Array.isArray(data) ? data : []);
      setAttachments(list);
      setErrorMessage('');
    } catch (err) {
      console.error('Failed to load attachments:', err);
      setErrorMessage('Could not load task attachments.');
    } finally {
      setIsLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    fetchAttachments();
  }, [fetchAttachments]);

  const handleUploadFile = async (file) => {
    if (!file) return;

    if (file.size > MAX_BYTES) {
      setErrorMessage(`File size (${formatFileSize(file.size)}) exceeds the 10 MB maximum limit.`);
      return;
    }

    setErrorMessage('');
    setIsUploading(true);
    try {
      await attachmentsApi.uploadAttachment(taskId, file);
      await fetchAttachments();
    } catch (err) {
      setErrorMessage(err.message || 'File upload failed. Ensure file type is supported.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleUploadFile(e.target.files[0]);
      e.target.value = '';
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this attachment?')) return;
    try {
      await attachmentsApi.deleteAttachment(id);
      setAttachments((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      setErrorMessage(err.message || 'Failed to delete attachment.');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUploadFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="section-block">
      <div className="section-header-compact">
        <h4 className="section-title">
          <PaperclipIcon size={14} />
          <span>Attachments ({attachments.length})</span>
        </h4>
        <span className="caption text-muted">Up to 10MB</span>
      </div>

      {errorMessage && <div className="alert alert-danger">{errorMessage}</div>}

      {/* Upload Zone */}
      {canEdit && (
        <div
          className={`dropzone ${isDragging ? 'is-active' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id={`file-input-${taskId}`}
            onChange={handleFileInputChange}
            disabled={isUploading}
            className="sr-only"
          />
          <label htmlFor={`file-input-${taskId}`} className="dropzone-label">
            {isUploading ? (
              <LoadingSpinner text="Uploading..." size="small" />
            ) : (
              <>
                <UploadCloudIcon size={20} className="dropzone-icon" />
                <span className="dropzone-text">
                  <span className="text-primary font-medium">Click to upload</span> or drag and drop
                </span>
              </>
            )}
          </label>
        </div>
      )}

      {/* Attachments List */}
      {isLoading ? (
        <LoadingSpinner text="Loading files..." size="small" />
      ) : attachments.length === 0 ? (
        <p className="empty-subtle">No attachments uploaded</p>
      ) : (
        <div className="attachments-list">
          {attachments.map((item) => (
            <div key={item.id} className="attachment-row">
              <div className="attachment-main">
                <a
                  href={item.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="attachment-filename"
                  title="Open file"
                >
                  {item.file_name}
                </a>
                <span className="caption text-muted">
                  {formatFileSize(item.file_size_bytes)} · {item.uploader_username || 'Member'} · {new Date(item.uploaded_at).toLocaleDateString()}
                </span>
              </div>
              <div className="attachment-actions">
                <a
                  href={item.file_url}
                  download
                  className="btn-icon"
                  title="Download"
                >
                  <DownloadIcon size={14} />
                </a>
                {canEdit && (
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="btn-icon btn-icon-danger"
                    title="Delete"
                  >
                    <TrashIcon size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
