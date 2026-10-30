import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authApi } from '../api/auth';
import { getAccessToken, clearTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProfile = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return null;
    }

    try {
      setIsLoading(true);
      const profile = await authApi.getCurrentUser();
      setUser(profile);
      setError(null);
      return profile;
    } catch (err) {
      console.warn('Failed to fetch user profile:', err);
      // If token is invalid or expired
      if (err.status === 401) {
        clearTokens();
        setUser(null);
      }
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProfile();

    const handleAuthExpired = () => {
      setUser(null);
    };

    window.addEventListener('auth:expired', handleAuthExpired);
    return () => window.removeEventListener('auth:expired', handleAuthExpired);
  }, [fetchProfile]);

  const login = async (username, password) => {
    setError(null);
    setIsLoading(true);
    try {
      await authApi.login(username, password);
      const profile = await authApi.getCurrentUser();
      setUser(profile);
      return profile;
    } catch (err) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    setError(null);
  };

  // RBAC permission helpers
  const isAdmin = user?.role === 'ADMIN' || user?.is_superuser === true;
  const isViewer = user?.role === 'VIEWER';
  const isContributor = user?.role === 'CONTRIBUTOR';
  const canEdit = !isViewer;

  const value = {
    user,
    isAuthenticated: Boolean(user),
    isLoading,
    error,
    login,
    logout,
    refreshUser: fetchProfile,
    isAdmin,
    isViewer,
    isContributor,
    canEdit,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

