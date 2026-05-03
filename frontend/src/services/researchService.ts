import type { ResearchRequest, StreamMessage, ContentBrief } from '../types';
import { config, getApiUrl } from '../config';

async function streamFetch(
  url: string,
  request: object,
  onMessage: (msg: StreamMessage) => void,
  onError: (err: string) => void
): Promise<void> {
  try {
    console.log('API call:', url);
    const response = await fetch(url, {
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
};
