import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useNotifications } from '../../context/NotificationContext';
import { BellIcon } from '../common/Icons';

export default function NotificationDropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, unreadCount, markAsRead, markAllAsRead, isLoading } = useNotifications();
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const recentNotifications = notifications.slice(0, 5);

  return (
    <div className="notif-wrapper" ref={dropdownRef}>
      <button
        className="btn-icon"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
        title="Notifications"
      >
        <BellIcon size={16} />
        {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className="notif-popover">
          <div className="notif-header">
            <span className="notif-title">Notifications</span>
            {unreadCount > 0 && (
              <button className="notif-action-btn" onClick={markAllAsRead}>
                Mark all read
              </button>
            )}
          </div>

          <div className="notif-list">
            {isLoading && recentNotifications.length === 0 ? (
              <div className="notif-empty">Loading...</div>
            ) : recentNotifications.length === 0 ? (
              <div className="notif-empty">No notifications</div>
            ) : (
              recentNotifications.map((notif) => (
                <div
                  key={notif.id}
                  className={`notif-item ${notif.is_read ? 'is-read' : 'is-unread'}`}
                  onClick={() => !notif.is_read && markAsRead(notif.id)}
                >
                  <div className="notif-item-header">
                    <span className="notif-type">{notif.notification_type?.replace('_', ' ')}</span>
                    <span className="notif-time">
                      {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="notif-text">{notif.message}</p>
                  {notif.task && (
                    <Link
                      to={`/tasks/${notif.task}`}
                      className="notif-link"
                      onClick={() => setIsOpen(false)}
                    >
                      Task #{notif.task} →
                    </Link>
                  )}
                </div>
              ))
            )}
          </div>

          <div className="notif-footer">
            <Link
              to="/notifications"
              className="notif-view-all"
              onClick={() => setIsOpen(false)}
            >
              View all notifications
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
