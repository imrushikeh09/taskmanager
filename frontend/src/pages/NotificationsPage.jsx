import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { notificationsApi } from '../api/notifications';
import { useNotifications } from '../context/NotificationContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import Toast from '../components/common/Toast';
import { CheckIcon, ArrowRightIcon } from '../components/common/Icons';

export default function NotificationsPage() {
  const { fetchNotifications: refreshGlobalNotifs } = useNotifications();

  const [notifications, setNotifications] = useState([]);
  const [filter, setFilter] = useState('ALL'); // 'ALL' or 'UNREAD'
  const [isLoading, setIsLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const loadNotifications = useCallback(async () => {
    try {
      setIsLoading(true);
      const params = {};
      if (filter === 'UNREAD') params.is_read = false;

      const res = await notificationsApi.listNotifications(params);
      const list = res.results || (Array.isArray(res) ? res : []);
      setNotifications(list);
    } catch (err) {
      console.error('Failed to load notifications:', err);
      setToast({ message: err.message || 'Could not load notifications.', type: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const handleMarkAsRead = async (id) => {
    try {
      await notificationsApi.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      refreshGlobalNotifs();
    } catch (err) {
      setToast({ message: err.message || 'Failed to update notification.', type: 'error' });
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      refreshGlobalNotifs();
      setToast({ message: 'All notifications marked as read.', type: 'success' });
    } catch (err) {
      setToast({ message: err.message || 'Failed to mark all as read.', type: 'error' });
    }
  };

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="page-shell">
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="page-subtitle">
            System activity, task assignments, and status updates.
          </p>
        </div>

        {unreadCount > 0 && (
          <button className="btn btn-secondary btn-sm" onClick={handleMarkAllAsRead}>
            <CheckIcon size={14} />
            <span>Mark all as read</span>
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="tab-group mb-4">
        <button
          className={`tab-btn ${filter === 'ALL' ? 'active' : ''}`}
          onClick={() => setFilter('ALL')}
        >
          All ({notifications.length})
        </button>
        <button
          className={`tab-btn ${filter === 'UNREAD' ? 'active' : ''}`}
          onClick={() => setFilter('UNREAD')}
        >
          Unread {unreadCount > 0 && `(${unreadCount})`}
        </button>
      </div>

      {/* Notifications List */}
      {isLoading ? (
        <LoadingSpinner text="Fetching notifications..." />
      ) : notifications.length === 0 ? (
        <EmptyState
          title="All caught up"
          description={
            filter === 'UNREAD'
              ? 'No unread notifications at the moment.'
              : 'Notifications about assignments and status changes will appear here.'
          }
        />
      ) : (
        <div className="card notifications-card">
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className={`notification-item ${notif.is_read ? 'is-read' : 'is-unread'}`}
            >
              <div className="notif-indicator">
                <span className={`status-dot ${notif.is_read ? 'dot-read' : 'dot-unread'}`}></span>
              </div>

              <div className="notif-content">
                <div className="notif-topline">
                  <span className="badge badge-subtle">{notif.notification_type?.replace('_', ' ')}</span>
                  <span className="caption text-muted">
                    {new Date(notif.created_at).toLocaleString()}
                  </span>
                </div>

                <p className="notif-body-text">{notif.message}</p>

                {notif.task && (
                  <Link to={`/tasks/${notif.task}`} className="link-subtle notif-task-link">
                    <span>View Task #{notif.task}</span>
                    <ArrowRightIcon size={12} />
                  </Link>
                )}
              </div>

              <div className="notif-action-cell">
                {!notif.is_read ? (
                  <button
                    className="btn btn-ghost btn-xs"
                    onClick={() => handleMarkAsRead(notif.id)}
                    title="Mark as read"
                  >
                    Mark read
                  </button>
                ) : (
                  <span className="caption text-muted">Read</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
