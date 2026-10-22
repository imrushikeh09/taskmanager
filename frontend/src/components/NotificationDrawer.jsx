import React from "react";
import { X, CheckCheck, Bell, Clock } from "lucide-react";
import { markNotificationAsRead, markAllNotificationsAsRead } from "../services/api";

export default function NotificationDrawer({
  isOpen,
  onClose,
  notifications = [],
  onRefreshNotifications,
}) {
  if (!isOpen) return null;

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const handleMarkAsRead = async (id) => {
    try {
      await markNotificationAsRead(id);
      if (onRefreshNotifications) onRefreshNotifications();
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead();
      if (onRefreshNotifications) onRefreshNotifications();
    } catch (err) {
      console.error("Failed to mark all notifications as read:", err);
    }
  };

  const formatTimestamp = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 110,
        background: "rgba(0, 0, 0, 0.4)",
      }}
      onClick={onClose}
    >
      <div className="notification-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div
          style={{
            padding: "1rem 1.25rem",
            borderBottom: "1px solid var(--border-subtle)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Bell size={15} style={{ color: "var(--brand-primary)" }} />
            <span style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-primary)" }}>
              Notifications
            </span>
            {unreadCount > 0 && (
              <span
                style={{
                  fontSize: "10px",
                  fontWeight: 700,
                  padding: "1px 5px",
                  borderRadius: "var(--radius-xs)",
                  background: "var(--priority-urgent-bg)",
                  color: "var(--priority-urgent)",
                }}
              >
                {unreadCount} unread
              </span>
            )}
          </div>

          <button className="modal-close-btn" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Action bar */}
        {unreadCount > 0 && (
          <div
            style={{
              padding: "0.5rem 1.25rem",
              borderBottom: "1px solid var(--border-subtle)",
              display: "flex",
              justifyContent: "flex-end",
            }}
          >
            <button
              className="btn btn-secondary"
              style={{ fontSize: "11px", padding: "0.2rem 0.5rem" }}
              onClick={handleMarkAllAsRead}
            >
              <CheckCheck size={12} />
              <span>Mark all as read</span>
            </button>
          </div>
        )}

        {/* List */}
        <div style={{ flex: 1, overflowY: "auto" }}>
          {notifications.length === 0 ? (
            <div
              style={{
                padding: "3rem 1.5rem",
                textAlign: "center",
                color: "var(--text-muted)",
                fontSize: "12px",
              }}
            >
              No notifications
            </div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                className={`notification-row ${!n.is_read ? "unread" : ""}`}
                style={{ cursor: !n.is_read ? "pointer" : "default" }}
                onClick={() => !n.is_read && handleMarkAsRead(n.id)}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "baseline",
                    marginBottom: "0.25rem",
                  }}
                >
                  <strong style={{ color: "var(--text-primary)", fontSize: "12px" }}>
                    {n.title}
                  </strong>
                  {!n.is_read && (
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "var(--radius-full)",
                        background: "var(--brand-primary)",
                      }}
                    />
                  )}
                </div>

                <p style={{ color: "var(--text-secondary)", fontSize: "12px", marginBottom: "0.35rem" }}>
                  {n.message}
                </p>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.25rem",
                    fontSize: "10px",
                    color: "var(--text-muted)",
                  }}
                >
                  <Clock size={10} />
                  <span>{formatTimestamp(n.created_at)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
