import type { ResearchRequest, StreamMessage } from '../types';
import { config, getApiUrl } from '../config';

export const researchService = {
  async callStageAResearch(
    request: ResearchRequest,
    onMessage: (msg: StreamMessage) => void,
    onError: (err: string) => void
  ): Promise<void> {
    try {
      console.log('API response :');
      const response = await fetch(getApiUrl(config.api.endpoints.stageAResearch), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      console.log('API response :', response);

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
  },
};
