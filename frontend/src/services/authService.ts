/**
 * Authentication Service
 * Handles user login, registration, token management, and Google OAuth
 */

import { getApiUrl } from '../config';

// Local storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_data';
const EXPIRES_IN_KEY = 'token_expires_in';

export interface User {
  id: string;
  username?: string;
  email?: string;
  name?: string;
}

export interface AuthResponse {
  status: string;
  message: string;
  access_token?: string;
  token_type?: string;
  expires_in?: number;
  user?: User;
}

class AuthService {
  /**
   * Register a new user with username and password
   */
  async register(
    username: string,
    password: string,
    name?: string
  ): Promise<AuthResponse> {
    try {
      const url = getApiUrl('/api/auth/register');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({
          username,
          password,
          name: name || username,
        }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        this.setToken(data.access_token, data.expires_in);
        if (data.user) {
          this.setUser(data.user);
        }
        return data;
      }

      throw new Error(data.message || 'Registration failed');
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Login with username and password
   */
  async login(username: string, password: string): Promise<AuthResponse> {
    try {
      const url = getApiUrl('/api/auth/login');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({
          username,
          password,
        }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        this.setToken(data.access_token, data.expires_in);
        if (data.user) {
          this.setUser(data.user);
        }
        return data;
      }

      throw new Error(data.message || 'Login failed');
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Login with Google OAuth token
   */
  async loginWithGoogle(googleToken: string, name?: string): Promise<AuthResponse> {
    try {
      const url = getApiUrl('/api/auth/google-login');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({
          token: googleToken,
          name: name || 'User',
        }),
      });

      const data = await response.json();

      if (response.ok && data.access_token) {
        this.setToken(data.access_token, data.expires_in);
        if (data.user) {
          this.setUser(data.user);
        }
        return data;
      }

      throw new Error(data.message || 'Google login failed');
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    }
  }

  /**
   * Verify if a token is still valid
   */
  async verifyToken(token?: string): Promise<boolean> {
    try {
      const tokenToVerify = token || this.getToken();
      if (!tokenToVerify) return false;

      const url = getApiUrl('/api/auth/verify-token');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true',
        },
        body: JSON.stringify({
          token: tokenToVerify,
        }),
      });

      return response.ok;
    } catch (error) {
      console.error('Token verification error:', error);
      return false;
    }
  }

  /**
   * Set authentication token in local storage
   */
  setToken(token: string, expiresIn?: number): void {
    localStorage.setItem(TOKEN_KEY, token);
    if (expiresIn) {
      const expiresAt = Date.now() + expiresIn * 1000;
      localStorage.setItem(EXPIRES_IN_KEY, expiresAt.toString());
    }
  }

  /**
   * Get authentication token from local storage
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  /**
   * Check if token is expired
   */
  isTokenExpired(): boolean {
    const expiresAt = localStorage.getItem(EXPIRES_IN_KEY);
    if (!expiresAt) return false;
    return Date.now() > parseInt(expiresAt, 10);
  }

  /**
   * Set user data in local storage
   */
  setUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Get user data from local storage
   */
  getUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    return !!token && !this.isTokenExpired();
  }

  /**
   * Logout and clear authentication data
   */
  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(EXPIRES_IN_KEY);
  }

  /**
   * Get authorization header for API requests
   */
  getAuthHeader(): Record<string, string> {
    const token = this.getToken();
    if (!token) {
      return {};
    }
    return {
      Authorization: `Bearer ${token}`,
    };
  }
}

export const authService = new AuthService();
