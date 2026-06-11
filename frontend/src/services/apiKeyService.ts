/**
 * API Key Service
 * Handles CRUD operations for user's custom API keys
 * Includes AES encryption/decryption for sensitive data
 */

import { getApiUrl } from '../config';
import { authService } from './authService';

// ─── AES Encryption (lightweight, browser-native) ──────────────────
// Using AES-GCM via Web Crypto API with a fixed passphrase-derived key.
// This is "light" encryption as requested — not for high-security, but
// ensures keys aren't stored as plain text.

const ENCRYPTION_PASSPHRASE = 'MarketMind-AI-2026-UserKeys';

async function getEncryptionKey(): Promise<CryptoKey> {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(ENCRYPTION_PASSPHRASE),
    { name: 'PBKDF2' },
    false,
    ['deriveKey']
  );

  return crypto.subtle.deriveKey(
    {
      name: 'PBKDF2',
      salt: encoder.encode('marketmind-salt'),
      iterations: 1000,
      hash: 'SHA-256',
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  );
}

export async function encryptValue(plainText: string): Promise<string> {
  if (!plainText) return '';
  try {
    const key = await getEncryptionKey();
    const encoder = new TextEncoder();
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      encoder.encode(plainText)
    );
    // Combine IV + ciphertext and encode as base64
    const combined = new Uint8Array(iv.length + new Uint8Array(encrypted).length);
    combined.set(iv);
    combined.set(new Uint8Array(encrypted), iv.length);
    return btoa(String.fromCharCode(...combined));
  } catch (err) {
    console.error('Encryption error:', err);
    return plainText; // Fallback to plain text
  }
}

export async function decryptValue(encryptedBase64: string): Promise<string> {
  if (!encryptedBase64) return '';
  try {
    const key = await getEncryptionKey();
    const combined = new Uint8Array(
      atob(encryptedBase64).split('').map(c => c.charCodeAt(0))
    );
    const iv = combined.slice(0, 12);
    const ciphertext = combined.slice(12);
    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      key,
      ciphertext
    );
    return new TextDecoder().decode(decrypted);
  } catch (err) {
    console.error('Decryption error:', err);
    return encryptedBase64; // Return as-is if decryption fails
  }
}

// ─── Types ─────────────────────────────────────────────────────────

export interface DiscordWebhook {
  id: string;
  name: string;
  url: string;          // Plain text (local only, never sent to server unencrypted)
  url_encrypted?: string; // AES encrypted (for storage)
  url_masked?: string;    // Masked for display
  is_default?: boolean;
  created_at?: string;
}

export interface UserApiKeys {
  discord_webhooks: DiscordWebhook[];
  gemini_api_key: string;
  has_gemini_key: boolean;
  gemini_api_key_masked: string;
  image_gen_api_key: string;
  has_image_gen_key: boolean;
  image_gen_api_key_masked: string;
}

// ─── API Fetch Helper ──────────────────────────────────────────────

const apiFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const customInit = { ...init };
  customInit.headers = {
    'ngrok-skip-browser-warning': 'true',
    ...authService.getAuthHeader(),
    ...customInit.headers,
  };
  return fetch(input, customInit);
};

// ─── Service ───────────────────────────────────────────────────────

class ApiKeyService {
  /**
   * Get current user's API keys
   */
  async getApiKeys(): Promise<UserApiKeys | null> {
    try {
      const url = getApiUrl('/api/user/api-keys');
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to get API keys:', err);
      return null;
    }
  }

  /**
   * Update user's API keys
   * Encrypts values before sending to backend
   */
  async updateApiKeys(data: {
    discord_webhooks?: { id: string; name: string; url: string; created_at?: string }[];
    gemini_api_key?: string;
    image_gen_api_key?: string;
  }): Promise<boolean> {
    try {
      const payload: Record<string, unknown> = {};

      // Encrypt discord webhook URLs
      if (data.discord_webhooks) {
        const encryptedWebhooks = await Promise.all(
          data.discord_webhooks.map(async (wh) => ({
            id: wh.id,
            name: wh.name,
            url: await encryptValue(wh.url),
            created_at: wh.created_at || new Date().toISOString(),
          }))
        );
        payload.discord_webhooks = encryptedWebhooks;
      }

      // Encrypt Gemini API key
      if (data.gemini_api_key !== undefined) {
        payload.gemini_api_key = data.gemini_api_key
          ? await encryptValue(data.gemini_api_key)
          : '';
      }

      // Encrypt Image Gen API key
      if (data.image_gen_api_key !== undefined) {
        payload.image_gen_api_key = data.image_gen_api_key
          ? await encryptValue(data.image_gen_api_key)
          : '';
      }

      const url = getApiUrl('/api/user/api-keys');
      const response = await apiFetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return response.ok;
    } catch (err) {
      console.error('Failed to update API keys:', err);
      return false;
    }
  }

  /**
   * Delete a specific API key
   */
  async deleteApiKey(keyType: string): Promise<boolean> {
    try {
      const url = getApiUrl(`/api/user/api-keys/${keyType}`);
      const response = await apiFetch(url, { method: 'DELETE' });
      return response.ok;
    } catch (err) {
      console.error('Failed to delete API key:', err);
      return false;
    }
  }

  /**
   * Get all available Discord webhooks (default + custom)
   */
  async getDiscordWebhooks(): Promise<DiscordWebhook[]> {
    try {
      const url = getApiUrl('/api/user/api-keys/discord-webhooks');
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data?.webhooks || [];
      }
      return [];
    } catch (err) {
      console.error('Failed to get webhooks:', err);
      return [];
    }
  }

  /**
   * Probe a Discord webhook URL to get channel name
   */
  async probeWebhook(webhookUrl: string): Promise<string> {
    try {
      const url = getApiUrl('/api/user/api-keys/discord-webhooks/probe');
      const response = await apiFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: webhookUrl }),
      });
      if (response.ok) {
        const data = await response.json();
        return data.data?.channel_name || '';
      }
      return '';
    } catch (err) {
      console.error('Failed to probe webhook:', err);
      return '';
    }
  }

  /**
   * Decrypt an encrypted value (for displaying in forms)
   */
  async decrypt(encrypted: string): Promise<string> {
    return decryptValue(encrypted);
  }
}

export const apiKeyService = new ApiKeyService();
