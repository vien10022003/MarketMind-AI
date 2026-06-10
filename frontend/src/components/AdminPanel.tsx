import { useState, useEffect, useCallback } from 'react';
import { adminService, type AdminUser } from '../services/adminService';
import './AdminPanel.css';

interface AdminPanelProps {
  onClose: () => void;
}

export default function AdminPanel({ onClose }: AdminPanelProps) {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [skip, setSkip] = useState(0);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const limit = 15;

  // Create user modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({ username: '', password: '', name: '', role: 'user' });
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  // Delete confirm
  const [deleteTarget, setDeleteTarget] = useState<AdminUser | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await adminService.getUsers(skip, limit, search);
      setUsers(data.users);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lỗi tải danh sách');
    } finally {
      setIsLoading(false);
    }
  }, [skip, search]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Search debounce
  const [searchInput, setSearchInput] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearch(searchInput);
      setSkip(0);
    }, 400);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError('');
    setIsCreating(true);
    try {
      await adminService.createUser({
        username: createForm.username,
        password: createForm.password,
        name: createForm.name || createForm.username,
        role: createForm.role,
      });
      setShowCreateModal(false);
      setCreateForm({ username: '', password: '', name: '', role: 'user' });
      await fetchUsers();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Lỗi tạo người dùng');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await adminService.deleteUser(deleteTarget.id);
      setDeleteTarget(null);
      await fetchUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Lỗi xóa người dùng');
      setDeleteTarget(null);
    } finally {
      setIsDeleting(false);
    }
  };

  const totalPages = Math.ceil(total / limit);
  const currentPage = Math.floor(skip / limit) + 1;

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '—';
    try {
      return new Date(dateStr).toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="admin-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="admin-panel">
        {/* Header */}
        <div className="admin-panel-header">
          <h2>👥 Quản lý người dùng</h2>
          <button className="admin-close-btn" onClick={onClose} title="Đóng">✕</button>
        </div>

        {/* Toolbar */}
        <div className="admin-toolbar">
          <input
            className="admin-search"
            type="text"
            placeholder="Tìm kiếm theo tên, email..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button className="admin-add-btn" onClick={() => setShowCreateModal(true)}>
            ＋ Thêm người dùng
          </button>
          <span className="admin-user-count">{total} người dùng</span>
        </div>

        {/* Error */}
        {error && <div className="admin-error">{error}</div>}

        {/* Table */}
        {isLoading ? (
          <div className="admin-loading">
            <div className="admin-loading-spinner" />
            <p>Đang tải...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="admin-empty">
            <div className="admin-empty-icon">🔍</div>
            <p>{search ? 'Không tìm thấy người dùng nào' : 'Chưa có người dùng nào'}</p>
          </div>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Tên</th>
                  <th>Username / Email</th>
                  <th>Vai trò</th>
                  <th>Đăng nhập</th>
                  <th>Ngày tạo</th>
                  <th>Lần đăng nhập cuối</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td title={user.name}>{user.name || '—'}</td>
                    <td title={user.username || user.email}>
                      {user.username || user.email || '—'}
                    </td>
                    <td>
                      <span className={`admin-role-badge admin-role-badge--${user.role}`}>
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className="admin-method-badge">
                        {user.auth_method === 'google' ? '🔵 Google' : '🔑 Password'}
                      </span>
                    </td>
                    <td>{formatDate(user.created_at)}</td>
                    <td>{formatDate(user.last_login)}</td>
                    <td>
                      <button
                        className="admin-delete-btn"
                        onClick={() => setDeleteTarget(user)}
                        title="Xóa người dùng"
                      >
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer / Pagination */}
        {total > limit && (
          <div className="admin-panel-footer">
            <span>Trang {currentPage} / {totalPages}</span>
            <div className="admin-pagination">
              <button
                className="admin-page-btn"
                disabled={skip === 0}
                onClick={() => setSkip(Math.max(0, skip - limit))}
              >
                ← Trước
              </button>
              <button
                className="admin-page-btn"
                disabled={skip + limit >= total}
                onClick={() => setSkip(skip + limit)}
              >
                Sau →
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="admin-modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) setShowCreateModal(false); }}>
          <div className="admin-modal">
            <h3>Thêm người dùng mới</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label htmlFor="admin-username">Tên đăng nhập *</label>
                <input
                  id="admin-username"
                  type="text"
                  placeholder="username"
                  value={createForm.username}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, username: e.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="admin-password">Mật khẩu *</label>
                <input
                  id="admin-password"
                  type="password"
                  placeholder="Tối thiểu 6 ký tự"
                  value={createForm.password}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, password: e.target.value }))}
                  required
                  minLength={6}
                />
              </div>
              <div className="form-group">
                <label htmlFor="admin-name">Tên hiển thị</label>
                <input
                  id="admin-name"
                  type="text"
                  placeholder="Tùy chọn"
                  value={createForm.name}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
                />
              </div>
              <div className="form-group">
                <label htmlFor="admin-role">Vai trò</label>
                <select
                  id="admin-role"
                  value={createForm.role}
                  onChange={(e) => setCreateForm(prev => ({ ...prev, role: e.target.value }))}
                >
                  <option value="user">User</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              {createError && <div className="admin-error">{createError}</div>}

              <div className="admin-modal-actions">
                <button type="button" className="admin-modal-cancel" onClick={() => setShowCreateModal(false)}>
                  Hủy
                </button>
                <button type="submit" className="admin-modal-submit" disabled={isCreating}>
                  {isCreating ? 'Đang tạo...' : 'Tạo người dùng'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirm Dialog */}
      {deleteTarget && (
        <div className="admin-confirm-overlay" onClick={(e) => { if (e.target === e.currentTarget) setDeleteTarget(null); }}>
          <div className="admin-confirm-dialog">
            <p>Bạn có chắc muốn xóa người dùng</p>
            <p><span className="confirm-username">{deleteTarget.username || deleteTarget.email || deleteTarget.name}</span>?</p>
            <small>Hành động này không thể hoàn tác.</small>
            <div className="admin-confirm-actions">
              <button className="admin-confirm-cancel" onClick={() => setDeleteTarget(null)}>
                Hủy
              </button>
              <button className="admin-confirm-delete" onClick={handleDelete} disabled={isDeleting}>
                {isDeleting ? 'Đang xóa...' : 'Xóa'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
