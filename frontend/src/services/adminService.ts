/**
 * Admin Service
 * Handles admin API calls for user management
 */

import { getApiUrl } from '../config';
import { authService } from './authService';

// Custom fetch wrapper with auth headers
const adminFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const customInit = { ...init };
  customInit.headers = {
    'ngrok-skip-browser-warning': 'true',
    ...authService.getAuthHeader(),
    ...customInit.headers,
  };
  return fetch(input, customInit);
};

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  name: string;
  role: string;
  auth_method: string;
  created_at: string;
  last_login: string;
}

export interface UsersListResponse {
  users: AdminUser[];
  total: number;
  skip: number;
  limit: number;
}

export const adminService = {
  /**
   * List all users with pagination and search
   */
  async getUsers(skip = 0, limit = 20, search = ''): Promise<UsersListResponse> {
    try {
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: limit.toString(),
      });
      if (search) params.set('search', search);

      const url = getApiUrl(`/api/admin/users?${params.toString()}`);
      const response = await adminFetch(url);

      if (response.ok) {
        const data = await response.json();
        return data.data || { users: [], total: 0, skip: 0, limit: 20 };
      }

      if (response.status === 403) {
        throw new Error('Không có quyền admin');
      }

      throw new Error(`HTTP ${response.status}`);
    } catch (err) {
      console.error('Failed to list users:', err);
      throw err;
    }
  },

  /**
   * Create a new user
   */
  async createUser(userData: {
    username: string;
    password: string;
    name?: string;
    role?: string;
  }): Promise<{ status: string; message: string; user?: AdminUser }> {
    try {
      const url = getApiUrl('/api/admin/users');
      const response = await adminFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error('Failed to create user:', err);
      throw err;
    }
  },

  /**
   * Delete a user by ID
   */
  async deleteUser(userId: string): Promise<{ status: string; message: string }> {
    try {
      const url = getApiUrl(`/api/admin/users/${userId}`);
      const response = await adminFetch(url, { method: 'DELETE' });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error('Failed to delete user:', err);
      throw err;
    }
  },
};
