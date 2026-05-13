import React, { useState } from 'react';
import { authService } from '../services/authService';
import GoogleLoginButton from './GoogleLoginButton';
import './AuthPage.css';

interface AuthPageProps {
  onAuthSuccess: () => void;
}

export default function AuthPage({ onAuthSuccess }: AuthPageProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      if (mode === 'register') {
        if (password !== confirmPassword) {
          throw new Error('Passwords do not match');
        }
        if (password.length < 6) {
          throw new Error('Password must be at least 6 characters');
        }
        await authService.register(username, password, name || username);
      } else {
        await authService.login(username, password);
      }

      // Clear form
      setUsername('');
      setPassword('');
      setConfirmPassword('');
      setName('');

      // Notify parent component
      onAuthSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = () => {
    setError('');
    onAuthSuccess();
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError('');
    setUsername('');
    setPassword('');
    setConfirmPassword('');
    setName('');
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🚀 MarketMind AI</h1>
          <p>
            {mode === 'login'
              ? 'Đăng nhập để bắt đầu'
              : 'Tạo tài khoản mới'}
          </p>
        </div>

        {/* Google Login */}
        <div className="auth-google-section">
          <GoogleLoginButton onSuccess={handleGoogleSuccess} />
        </div>

        {/* Divider */}
        <div className="auth-divider">
          <span>hoặc</span>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form">
          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="name">Tên hiển thị (tùy chọn)</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Nhập tên của bạn"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">Email hoặc Tên đăng nhập</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="user@example.com hoặc username"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mật khẩu</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu"
              required
              minLength={6}
            />
            {mode === 'register' && (
              <small>Tối thiểu 6 ký tự</small>
            )}
          </div>

          {mode === 'register' && (
            <div className="form-group">
              <label htmlFor="confirmPassword">Xác nhận mật khẩu</label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Xác nhận mật khẩu"
                required
              />
            </div>
          )}

          {error && <div className="auth-error">{error}</div>}

          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading
              ? 'Đang xử lý...'
              : mode === 'login'
              ? 'Đăng nhập'
              : 'Tạo tài khoản'}
          </button>
        </form>

        {/* Toggle Mode */}
        <div className="auth-toggle">
          <p>
            {mode === 'login'
              ? 'Chưa có tài khoản?'
              : 'Đã có tài khoản?'}{' '}
            <button
              type="button"
              onClick={toggleMode}
              className="auth-toggle-button"
            >
              {mode === 'login' ? 'Tạo ngay' : 'Đăng nhập'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
