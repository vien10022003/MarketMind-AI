/**
 * API Key Settings Modal
 * Manages per-user API keys: Discord webhooks, Gemini API key, Image Gen API key
 */

import { useState, useEffect, useCallback } from 'react';
import { apiKeyService, decryptValue, type DiscordWebhook } from '../services/apiKeyService';
import './ApiKeySettings.css';

interface ApiKeySettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabId = 'discord' | 'gemini' | 'imagegen';

export function ApiKeySettings({ isOpen, onClose }: ApiKeySettingsProps) {
  const [activeTab, setActiveTab] = useState<TabId>('discord');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  // Discord state
  const [webhooks, setWebhooks] = useState<DiscordWebhook[]>([]);
  const [defaultWebhookMasked, setDefaultWebhookMasked] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newWebhookName, setNewWebhookName] = useState('');
  const [newWebhookUrl, setNewWebhookUrl] = useState('');
  const [isProbing, setIsProbing] = useState(false);

  // Gemini state
  const [geminiKey, setGeminiKey] = useState('');
  const [geminiKeyMasked, setGeminiKeyMasked] = useState('');
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [showGeminiKey, setShowGeminiKey] = useState(false);
  const [isEditingGemini, setIsEditingGemini] = useState(false);

  // Image Gen state
  const [imageGenKey, setImageGenKey] = useState('');
  const [imageGenKeyMasked, setImageGenKeyMasked] = useState('');
  const [hasImageGenKey, setHasImageGenKey] = useState(false);
  const [showImageGenKey, setShowImageGenKey] = useState(false);
  const [isEditingImageGen, setIsEditingImageGen] = useState(false);

  // Load data
  const loadApiKeys = useCallback(async () => {
    setIsLoading(true);
    try {
      // Get webhooks (includes default)
      const allWebhooks = await apiKeyService.getDiscordWebhooks();
      const defaultWh = allWebhooks.find(w => w.is_default);
      const customWhs = allWebhooks.filter(w => !w.is_default);

      if (defaultWh) {
        setDefaultWebhookMasked(defaultWh.url_masked || '');
      }

      // Decrypt custom webhook URLs for local display
      const decryptedWebhooks: DiscordWebhook[] = await Promise.all(
        customWhs.map(async (wh) => ({
          ...wh,
          url: wh.url_encrypted ? await decryptValue(wh.url_encrypted) : '',
        }))
      );
      setWebhooks(decryptedWebhooks);

      // Get API keys
      const keys = await apiKeyService.getApiKeys();
      if (keys) {
        setHasGeminiKey(keys.has_gemini_key);
        setGeminiKeyMasked(keys.gemini_api_key_masked);
        setHasImageGenKey(keys.has_image_gen_key);
        setImageGenKeyMasked(keys.image_gen_api_key_masked);
      }
    } catch (err) {
      console.error('Failed to load API keys:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      loadApiKeys();
      setSaveMessage('');
    }
  }, [isOpen, loadApiKeys]);

  // ─── Discord Handlers ────────────────────────────────────────

  const handleProbeWebhook = async () => {
    if (!newWebhookUrl.trim()) return;
    setIsProbing(true);
    try {
      const channelName = await apiKeyService.probeWebhook(newWebhookUrl);
      if (channelName) {
        setNewWebhookName(channelName);
      }
    } finally {
      setIsProbing(false);
    }
  };

  const handleAddWebhook = async () => {
    if (!newWebhookUrl.trim()) return;
    const name = newWebhookName.trim() || 'Custom Webhook';

    const newWh: DiscordWebhook = {
      id: `wh-${Date.now()}`,
      name,
      url: newWebhookUrl.trim(),
      created_at: new Date().toISOString(),
    };

    const updatedWebhooks = [...webhooks, newWh];
    setWebhooks(updatedWebhooks);
    setNewWebhookName('');
    setNewWebhookUrl('');
    setShowAddForm(false);

    // Save to backend
    await saveWebhooks(updatedWebhooks);
  };

  const handleRemoveWebhook = async (id: string) => {
    const updatedWebhooks = webhooks.filter(w => w.id !== id);
    setWebhooks(updatedWebhooks);
    await saveWebhooks(updatedWebhooks);
  };

  const saveWebhooks = async (whs: DiscordWebhook[]) => {
    setIsSaving(true);
    try {
      const success = await apiKeyService.updateApiKeys({
        discord_webhooks: whs.map(w => ({
          id: w.id,
          name: w.name,
          url: w.url,
          created_at: w.created_at,
        })),
      });
      setSaveMessage(success ? '✅ Đã lưu!' : '❌ Lỗi khi lưu');
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  // ─── Gemini Handlers ─────────────────────────────────────────

  const handleSaveGeminiKey = async () => {
    setIsSaving(true);
    try {
      const success = await apiKeyService.updateApiKeys({
        gemini_api_key: geminiKey.trim(),
      });
      if (success) {
        setHasGeminiKey(!!geminiKey.trim());
        setGeminiKeyMasked(geminiKey.trim() ? `${'•'.repeat(Math.max(0, geminiKey.trim().length - 4))}${geminiKey.trim().slice(-4)}` : '');
        setIsEditingGemini(false);
        setGeminiKey('');
        setSaveMessage('✅ Gemini API Key đã lưu!');
      } else {
        setSaveMessage('❌ Lỗi khi lưu');
      }
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  const handleDeleteGeminiKey = async () => {
    setIsSaving(true);
    try {
      const success = await apiKeyService.deleteApiKey('gemini_api_key');
      if (success) {
        setHasGeminiKey(false);
        setGeminiKeyMasked('');
        setGeminiKey('');
        setIsEditingGemini(false);
        setSaveMessage('✅ Đã xóa Gemini API Key');
      }
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  // ─── Image Gen Handlers ──────────────────────────────────────

  const handleSaveImageGenKey = async () => {
    setIsSaving(true);
    try {
      const success = await apiKeyService.updateApiKeys({
        image_gen_api_key: imageGenKey.trim(),
      });
      if (success) {
        setHasImageGenKey(!!imageGenKey.trim());
        setImageGenKeyMasked(imageGenKey.trim() ? `${'•'.repeat(Math.max(0, imageGenKey.trim().length - 4))}${imageGenKey.trim().slice(-4)}` : '');
        setIsEditingImageGen(false);
        setImageGenKey('');
        setSaveMessage('✅ Image Gen API Key đã lưu!');
      } else {
        setSaveMessage('❌ Lỗi khi lưu');
      }
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  const handleDeleteImageGenKey = async () => {
    setIsSaving(true);
    try {
      const success = await apiKeyService.deleteApiKey('image_gen_api_key');
      if (success) {
        setHasImageGenKey(false);
        setImageGenKeyMasked('');
        setImageGenKey('');
        setIsEditingImageGen(false);
        setSaveMessage('✅ Đã xóa Image Gen API Key');
      }
    } finally {
      setIsSaving(false);
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="apikey-modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="apikey-modal">
        {/* Header */}
        <div className="apikey-modal-header">
          <h2>⚙️ Quản lý API Keys</h2>
          <button className="apikey-modal-close" onClick={onClose}>✕</button>
        </div>

        {/* Tabs */}
        <div className="apikey-tabs">
          <button
            className={`apikey-tab ${activeTab === 'discord' ? 'active' : ''}`}
            onClick={() => setActiveTab('discord')}
          >
            <span className="apikey-tab-icon">💬</span>
            Discord Webhooks
          </button>
          <button
            className={`apikey-tab ${activeTab === 'gemini' ? 'active' : ''}`}
            onClick={() => setActiveTab('gemini')}
          >
            <span className="apikey-tab-icon">🤖</span>
            LLM (Gemini)
          </button>
          <button
            className={`apikey-tab ${activeTab === 'imagegen' ? 'active' : ''}`}
            onClick={() => setActiveTab('imagegen')}
          >
            <span className="apikey-tab-icon">🎨</span>
            Image Gen
          </button>
        </div>

        {/* Body */}
        <div className="apikey-modal-body">
          {isLoading ? (
            <div className="apikey-loading">
              <div className="apikey-loading-spinner" />
              <span>Đang tải...</span>
            </div>
          ) : (
            <>
              {/* ═══ Discord Tab ═══ */}
              {activeTab === 'discord' && (
                <div>
                  <div className="apikey-section">
                    <div className="apikey-section-title">Discord Webhook URLs</div>
                    <p className="apikey-section-desc">
                      Webhook dùng để đăng bài lên Discord channel. Bạn có thể sử dụng webhook mặc định hoặc thêm webhook riêng cho các channel khác nhau.
                    </p>
                  </div>

                  <div className="apikey-webhook-list">
                    {/* Default webhook */}
                    {defaultWebhookMasked && (
                      <div className="apikey-webhook-item apikey-webhook-item--default">
                        <div className="apikey-webhook-header">
                          <span className="apikey-webhook-name">🏠 Mặc định (Hệ thống)</span>
                          <span className="apikey-webhook-badge apikey-webhook-badge--default">Default</span>
                        </div>
                        <div className="apikey-webhook-url">{defaultWebhookMasked}</div>
                      </div>
                    )}

                    {/* Custom webhooks */}
                    {webhooks.map((wh) => (
                      <div key={wh.id} className="apikey-webhook-item">
                        <div className="apikey-webhook-header">
                          <span className="apikey-webhook-name">📌 {wh.name}</span>
                          <span className="apikey-webhook-badge apikey-webhook-badge--custom">Custom</span>
                        </div>
                        <div className="apikey-webhook-url">
                          {showGeminiKey ? wh.url : (wh.url_masked || `...${wh.url.slice(-12)}`)}
                        </div>
                        <div className="apikey-webhook-actions">
                          <button
                            className="apikey-btn apikey-btn--danger"
                            onClick={() => handleRemoveWebhook(wh.id)}
                            disabled={isSaving}
                          >
                            🗑️ Xóa
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Add webhook form */}
                  {!showAddForm ? (
                    <div style={{ marginTop: 12 }}>
                      <button
                        className="apikey-btn apikey-btn--secondary"
                        onClick={() => setShowAddForm(true)}
                      >
                        ➕ Thêm Webhook
                      </button>
                    </div>
                  ) : (
                    <div className="apikey-add-webhook">
                      <div className="apikey-add-webhook-fields">
                        <div className="apikey-form-group">
                          <label>Webhook URL</label>
                          <div className="apikey-add-webhook-row">
                            <input
                              className="apikey-input"
                              type="url"
                              placeholder="https://discord.com/api/webhooks/..."
                              value={newWebhookUrl}
                              onChange={(e) => setNewWebhookUrl(e.target.value)}
                            />
                            <button
                              className="apikey-btn apikey-btn--secondary"
                              onClick={handleProbeWebhook}
                              disabled={isProbing || !newWebhookUrl.trim()}
                              title="Tự động lấy tên channel"
                            >
                              {isProbing ? '⏳' : '🔍'}
                            </button>
                          </div>
                        </div>
                        <div className="apikey-form-group">
                          <label>Tên hiển thị</label>
                          <input
                            className="apikey-input apikey-input--name"
                            type="text"
                            placeholder="VD: Channel Marketing, Server A..."
                            value={newWebhookName}
                            onChange={(e) => setNewWebhookName(e.target.value)}
                            style={{ maxWidth: '100%' }}
                          />
                        </div>
                      </div>
                      <div className="apikey-add-webhook-actions">
                        <button
                          className="apikey-btn apikey-btn--primary"
                          onClick={handleAddWebhook}
                          disabled={!newWebhookUrl.trim() || isSaving}
                        >
                          ✅ Thêm
                        </button>
                        <button
                          className="apikey-btn apikey-btn--secondary"
                          onClick={() => { setShowAddForm(false); setNewWebhookName(''); setNewWebhookUrl(''); }}
                        >
                          Hủy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ═══ Gemini Tab ═══ */}
              {activeTab === 'gemini' && (
                <div>
                  <div className="apikey-section">
                    <div className="apikey-provider-badge apikey-provider-badge--gemini">
                      <span>✦</span> Google Gemini API
                    </div>
                    <div className="apikey-section-title">API Key cho mô hình ngôn ngữ</div>
                    <p className="apikey-section-desc">
                      Nhập API key Google Gemini của bạn để sử dụng mô hình riêng. Nếu không nhập, hệ thống sẽ sử dụng key mặc định.
                      <br />
                      Lấy key tại: <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" style={{ color: '#60a5fa' }}>aistudio.google.com/apikey</a>
                    </p>
                  </div>

                  <div className={`apikey-status ${hasGeminiKey ? 'apikey-status--active' : 'apikey-status--inactive'}`}>
                    <span>{hasGeminiKey ? '🟢' : '⚪'}</span>
                    {hasGeminiKey ? 'Đã cấu hình key riêng' : 'Đang dùng key hệ thống'}
                  </div>

                  {!isEditingGemini ? (
                    <div>
                      {hasGeminiKey && (
                        <div className="apikey-form-group">
                          <label>API Key hiện tại</label>
                          <div className="apikey-input-wrapper">
                            <input
                              className="apikey-input"
                              type="text"
                              value={geminiKeyMasked}
                              disabled
                            />
                          </div>
                        </div>
                      )}
                      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                        <button
                          className="apikey-btn apikey-btn--primary"
                          onClick={() => setIsEditingGemini(true)}
                        >
                          {hasGeminiKey ? '✏️ Thay đổi' : '➕ Thêm API Key'}
                        </button>
                        {hasGeminiKey && (
                          <button
                            className="apikey-btn apikey-btn--danger"
                            onClick={handleDeleteGeminiKey}
                            disabled={isSaving}
                          >
                            🗑️ Xóa
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="apikey-form-group">
                        <label>Nhập Gemini API Key</label>
                        <div className="apikey-input-wrapper">
                          <input
                            className="apikey-input"
                            type={showGeminiKey ? 'text' : 'password'}
                            placeholder="AIzaSy..."
                            value={geminiKey}
                            onChange={(e) => setGeminiKey(e.target.value)}
                            autoFocus
                          />
                          <button
                            className="apikey-toggle-btn"
                            onClick={() => setShowGeminiKey(!showGeminiKey)}
                          >
                            {showGeminiKey ? '🙈' : '👁️'}
                          </button>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                        <button
                          className="apikey-btn apikey-btn--success"
                          onClick={handleSaveGeminiKey}
                          disabled={isSaving || !geminiKey.trim()}
                        >
                          {isSaving ? '⏳ Đang lưu...' : '💾 Lưu'}
                        </button>
                        <button
                          className="apikey-btn apikey-btn--secondary"
                          onClick={() => { setIsEditingGemini(false); setGeminiKey(''); }}
                        >
                          Hủy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ═══ Image Gen Tab ═══ */}
              {activeTab === 'imagegen' && (
                <div>
                  <div className="apikey-section">
                    <div className="apikey-provider-badge apikey-provider-badge--imagegen">
                      <span>🎨</span> Stable Diffusion API (Hugging Face)
                    </div>
                    <div className="apikey-section-title">API Key cho tạo ảnh AI</div>
                    <p className="apikey-section-desc">
                      API key từ Hugging Face dùng cho mô hình tạo ảnh Stable Diffusion.
                      Nếu không cấu hình, hệ thống sẽ bỏ qua bước tạo ảnh khi đăng bài.
                      <br />
                      Lấy key tại: <a href="https://huggingface.co/settings/tokens" target="_blank" rel="noopener noreferrer" style={{ color: '#fbbc04' }}>huggingface.co/settings/tokens</a>
                    </p>
                  </div>

                  <div className={`apikey-status ${hasImageGenKey ? 'apikey-status--active' : 'apikey-status--inactive'}`}>
                    <span>{hasImageGenKey ? '🟢' : '⚪'}</span>
                    {hasImageGenKey ? 'Đã cấu hình key' : 'Chưa cấu hình'}
                  </div>

                  {!isEditingImageGen ? (
                    <div>
                      {hasImageGenKey && (
                        <div className="apikey-form-group">
                          <label>API Key hiện tại</label>
                          <div className="apikey-input-wrapper">
                            <input
                              className="apikey-input"
                              type="text"
                              value={imageGenKeyMasked}
                              disabled
                            />
                          </div>
                        </div>
                      )}
                      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                        <button
                          className="apikey-btn apikey-btn--primary"
                          onClick={() => setIsEditingImageGen(true)}
                        >
                          {hasImageGenKey ? '✏️ Thay đổi' : '➕ Thêm API Key'}
                        </button>
                        {hasImageGenKey && (
                          <button
                            className="apikey-btn apikey-btn--danger"
                            onClick={handleDeleteImageGenKey}
                            disabled={isSaving}
                          >
                            🗑️ Xóa
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="apikey-form-group">
                        <label>Nhập Hugging Face API Token</label>
                        <div className="apikey-input-wrapper">
                          <input
                            className="apikey-input"
                            type={showImageGenKey ? 'text' : 'password'}
                            placeholder="hf_..."
                            value={imageGenKey}
                            onChange={(e) => setImageGenKey(e.target.value)}
                            autoFocus
                          />
                          <button
                            className="apikey-toggle-btn"
                            onClick={() => setShowImageGenKey(!showImageGenKey)}
                          >
                            {showImageGenKey ? '🙈' : '👁️'}
                          </button>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                        <button
                          className="apikey-btn apikey-btn--success"
                          onClick={handleSaveImageGenKey}
                          disabled={isSaving || !imageGenKey.trim()}
                        >
                          {isSaving ? '⏳ Đang lưu...' : '💾 Lưu'}
                        </button>
                        <button
                          className="apikey-btn apikey-btn--secondary"
                          onClick={() => { setIsEditingImageGen(false); setImageGenKey(''); }}
                        >
                          Hủy
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Save bar */}
        {saveMessage && (
          <div className="apikey-save-bar">
            <span className="apikey-save-status">{saveMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
}
