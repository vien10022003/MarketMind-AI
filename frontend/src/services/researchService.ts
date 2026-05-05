import type { ResearchRequest, StreamMessage, ContentBrief } from '../types';
import { config, getApiUrl } from '../config';

// Custom fetch wrapper to always include ngrok bypass headers
const apiFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const customInit = { ...init };
  customInit.headers = {
    ...customInit.headers,
    'ngrok-skip-browser-warning': 'true',
  };
  return fetch(input, customInit);
};

async function streamFetch(
  url: string,
  request: object,
  onMessage: (msg: StreamMessage) => void,
  onError: (err: string) => void
): Promise<void> {
  try {
    console.log('API call:', url);
    const response = await apiFetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    console.log('API response:', response);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Decode chunk and add to buffer
      buffer += decoder.decode(value, { stream: true });

      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.trim() === '') continue;

        try {
          const data = JSON.parse(line) as StreamMessage;
          onMessage(data);
        } catch (e) {
          console.error('Failed to parse JSON line:', line, e);
        }
      }
    }

    // Process any remaining buffer
    if (buffer.trim()) {
      try {
        const data = JSON.parse(buffer) as StreamMessage;
        onMessage(data);
      } catch (e) {
        console.error('Failed to parse final buffer:', buffer, e);
      }
    }
  } catch (err) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    onError(errorMsg);
  }
}

export const researchService = {
  /**
   * Main endpoint — handles chat, knowledge, and initial research classification
   */
  async callStageAResearch(
    request: ResearchRequest,
    onMessage: (msg: StreamMessage) => void,
    onError: (err: string) => void
  ): Promise<void> {
    const url = getApiUrl(config.api.endpoints.stageAResearch);
    return streamFetch(url, request, onMessage, onError);
  },

  /**
   * Marketing form submission — runs full Stage A pipeline (skips intent classification)
   */
  async callMarketingResearch(
    request: ResearchRequest,
    onMessage: (msg: StreamMessage) => void,
    onError: (err: string) => void
  ): Promise<void> {
    const url = getApiUrl(config.api.endpoints.stageAResearch + '/marketing');
    return streamFetch(url, request, onMessage, onError);
  },

  /**
   * Stage B — Generate marketing strategy from Stage A report
   */
  async callStageBStrategy(
    request: {
      stage_a_report: Record<string, unknown>;
      stage_a_input: Record<string, unknown>;
      mongodb_id?: string;
    },
    onMessage: (msg: StreamMessage) => void,
    onError: (err: string) => void
  ): Promise<void> {
    const url = getApiUrl(config.api.endpoints.stageBStrategy);
    return streamFetch(url, request, onMessage, onError);
  },

  /**
   * Stage B — Approve strategy and briefs
   */
  async approveStageBBriefs(
    request: {
      mongodb_id?: string;
      strategy: Record<string, unknown>;
      approved_briefs: ContentBrief[];
    }
  ): Promise<{ status: string; message: string; strategy_id?: string }> {
    const url = getApiUrl(config.api.endpoints.stageBApprove);
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });
      return await response.json();
    } catch (err) {
      return { status: 'error', message: String(err) };
    }
  },

  /**
   * Stage C — Execute campaign (image gen + Discord posting)
   */
  async callStageCCampaign(
    request: {
      approved_briefs: ContentBrief[];
      webhook_url?: string;
      image_api_url?: string;
      skip_image_generation?: boolean;
      mongodb_stage_a_id?: string;
    },
    onMessage: (msg: StreamMessage) => void,
    onError: (err: string) => void
  ): Promise<void> {
    const url = getApiUrl(config.api.endpoints.stageCCampaign);
    return streamFetch(url, request as object, onMessage, onError);
  },

  /**
   * Stage C — Schedule campaign (with specific posting times)
   */
  async callStageCCampaignScheduled(
    request: {
      approved_briefs: ContentBrief[];
      scheduled_times: string[]; // ISO 8601 datetimes
      webhook_url?: string;
      image_api_url?: string;
      skip_image_generation?: boolean;
      mongodb_stage_a_id?: string;
    },
    onMessage: (msg: StreamMessage) => void,
    onError: (err: string) => void
  ): Promise<void> {
    const url = getApiUrl(config.api.endpoints.stageCCampaign + '/scheduled');
    return streamFetch(url, request as object, onMessage, onError);
  },

  /**
   * Get scheduler status
   */
  async getSchedulerStatus(): Promise<{
    running: boolean;
    pending_briefs: number;
    check_interval: number;
  } | null> {
    try {
      const url = getApiUrl('/api/stage-c/scheduler/status');
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to get scheduler status:', err);
      return null;
    }
  },

  /**
   * Get all scheduled campaigns
   */
  async getScheduledCampaigns(status?: string): Promise<any[]> {
    try {
      const url = status
        ? getApiUrl(`/api/stage-c/scheduler/campaigns?status=${status}`)
        : getApiUrl('/api/stage-c/scheduler/campaigns');
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data?.campaigns || [];
      }
      return [];
    } catch (err) {
      console.error('Failed to get scheduled campaigns:', err);
      return [];
    }
  },

  /**
   * Get specific campaign details
   */
  async getCampaignDetails(campaignId: string): Promise<any | null> {
    try {
      const url = getApiUrl(`/api/stage-c/scheduler/campaigns/${campaignId}`);
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to get campaign details:', err);
      return null;
    }
  },

  /**
   * Get pending briefs ready to post
   */
  async getPendingBriefs(): Promise<any> {
    try {
      const url = getApiUrl('/api/stage-c/scheduler/pending');
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to get pending briefs:', err);
      return null;
    }
  },

  // ────────────────────────────────────────────────────────────
  // Conversation History APIs
  // ────────────────────────────────────────────────────────────

  /**
   * List all conversations
   */
  async listConversations(skip = 0, limit = 10): Promise<any> {
    try {
      const url = getApiUrl(`/api/conversations?skip=${skip}&limit=${limit}`);
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data || { conversations: [], total: 0 };
      }
      return { conversations: [], total: 0 };
    } catch (err) {
      console.error('Failed to list conversations:', err);
      return { conversations: [], total: 0 };
    }
  },

  /**
   * Get a specific conversation
   */
  async getConversation(conversationId: string): Promise<any | null> {
    try {
      const url = getApiUrl(`/api/conversations/${conversationId}`);
      const response = await apiFetch(url);
      if (response.ok) {
        const data = await response.json();
        return data.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to get conversation:', err);
      return null;
    }
  },

  /**
   * Create a new conversation
   */
  async createConversation(title?: string): Promise<any | null> {
    try {
      const url = getApiUrl('/api/conversations');
      const response = await apiFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      if (response.ok) {
        const data = await response.json();
        return data.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to create conversation:', err);
      return null;
    }
  },

  /**
   * Save messages to conversation
   */
  async saveMessagesToConversation(conversationId: string, messages: any[]): Promise<boolean> {
    try {
      const url = getApiUrl(`/api/conversations/${conversationId}/messages`);
      const response = await apiFetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages }),
      });
      return response.ok;
    } catch (err) {
      console.error('Failed to save messages:', err);
      return false;
    }
  },

  /**
   * Update conversation title
   */
  async updateConversationTitle(conversationId: string, title: string): Promise<boolean> {
    try {
      const url = getApiUrl(`/api/conversations/${conversationId}/title`);
      const response = await apiFetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title }),
      });
      return response.ok;
    } catch (err) {
      console.error('Failed to update title:', err);
      return false;
    }
  },

  /**
   * Delete a conversation
   */
  async deleteConversation(conversationId: string): Promise<boolean> {
    try {
      const url = getApiUrl(`/api/conversations/${conversationId}`);
      const response = await apiFetch(url, { method: 'DELETE' });
      return response.ok;
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      return false;
    }
  },
};
