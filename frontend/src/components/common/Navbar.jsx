import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import NotificationDropdown from '../notifications/NotificationDropdown';
import RoleBadge from './RoleBadge';
import { LayersIcon, LogoutIcon, SunIcon, MoonIcon } from './Icons';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="header-inner">
        {/* Left: Brand & Nav */}
        <div className="header-left">
          <Link to="/" className="brand-lockup">
            <div className="brand-mark">
              <LayersIcon size={16} />
            </div>
            <span className="brand-name">TaskManager</span>
          </Link>

          <nav className="header-nav">
            <NavLink
              to="/"
              end
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/tasks"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Tasks
            </NavLink>
            <NavLink
              to="/kanban"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Board
            </NavLink>
            <NavLink
              to="/projects"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Projects
            </NavLink>
          </nav>
        </div>

        {/* Right: Actions & User */}
        <div className="header-right">
          <button
            onClick={toggleTheme}
            className="btn-icon theme-toggle-btn"
            title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <MoonIcon size={16} /> : <SunIcon size={16} />}
          </button>

          {isAuthenticated ? (
            <>
              <NotificationDropdown />
              <div className="header-divider" />
              <div className="user-menu">
                <div className="user-avatar" title={user?.username}>
                  {(user?.first_name?.[0] || user?.username?.[0] || 'U').toUpperCase()}
                </div>
                <div className="user-meta">
                  <span className="user-name">{user?.username}</span>
                  <RoleBadge role={user?.role} />
                </div>
                <button
                  onClick={handleLogout}
                  className="btn-icon"
                  title="Sign out"
                  aria-label="Sign out"
                >
                  <LogoutIcon size={15} />
                </button>
              </div>
            </>
          ) : (
            <Link to="/login" className="btn btn-primary btn-sm">
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
