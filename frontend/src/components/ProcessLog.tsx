import { useState, useRef, useEffect } from 'react';
import type { ChatMessage, ResearchRequest, ContentBrief, ResearchReport } from '../types';
import { ChatMessageBubble } from './ChatMessage';

/**
 * A "process message" is any status, plan, react_summary, or evidence message
 * that appears during the research pipeline. These are grouped together into
 * a ProcessLog that shows only the latest status with a clickable indicator,
 * and expands to show all messages in the group when clicked.
 */

// Message types that belong inside the process log (hidden until expanded)
export const PROCESS_LOG_TYPES = new Set([
  'status',
  'plan',
  'react_summary',
  'evidence',
]);

// Check if a message type is part of the process log flow
export function isProcessLogMessage(type: string): boolean {
  return PROCESS_LOG_TYPES.has(type);
}

interface ProcessLogProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  onClarificationConfirm?: (overrides: Partial<ResearchRequest>) => void;
  onMarketingFormSubmit?: (formData: ResearchRequest) => void;
  onStartCampaign?: (approvedBriefs: ContentBrief[]) => void;
  onAcceptStageBProposal?: (reportData: ResearchReport, mongodbId?: string) => void;
  onAcceptStageCProposal?: (briefs: ContentBrief[]) => void;
  onAcceptStageCScheduleProposal?: (briefs: ContentBrief[], times: string[], mongodbId?: string) => void;
}

export function ProcessLog({
  messages,
  isLoading,
  onClarificationConfirm,
  onMarketingFormSubmit,
  onStartCampaign,
  onAcceptStageBProposal,
  onAcceptStageCProposal,
  onAcceptStageCScheduleProposal,
}: ProcessLogProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentHeight, setContentHeight] = useState(0);

  // Find the latest status message to display as the "current" status
  const latestStatus = [...messages].reverse().find((m) => m.type === 'status');
  const totalSteps = messages.filter((m) => m.type === 'status').length;
  const hasDetailMessages = messages.some((m) => m.type !== 'status');

  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight);
    }
  }, [isExpanded, messages]);

  // Auto-collapse when new messages arrive (so only the latest shows)
  useEffect(() => {
    setIsExpanded(false);
  }, [messages.length]);

  if (messages.length === 0) return null;

  return (
    <div className={`process-log ${isExpanded ? 'is-expanded' : ''}`}>
      {/* Current status indicator — always visible */}
      <button
        className="process-log-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <div className="process-log-indicator">
          <span className="process-log-pulse" />
          <span className="process-log-current">
            {latestStatus?.content || messages[messages.length - 1].content}
          </span>
        </div>
        <div className="process-log-meta">
          <span className="process-log-count">
            {totalSteps} bước{hasDetailMessages ? ' · có chi tiết' : ''}
          </span>
          <span className={`process-log-chevron ${isExpanded ? 'rotated' : ''}`}>
            ▾
          </span>
        </div>
      </button>

      {/* Expandable detail area */}
      <div
        className="process-log-body"
        style={{ maxHeight: isExpanded ? `${contentHeight}px` : '0px' }}
      >
        <div ref={contentRef} className="process-log-inner">
          <div className="process-log-timeline">
            {messages.map((msg) => (
              <div key={msg.id} className="process-log-entry">
                <div className="process-log-timeline-dot" data-type={msg.type} />
                <div className="process-log-entry-content">
                  <ChatMessageBubble
                    message={msg}
                    isLoading={isLoading}
                    onClarificationConfirm={onClarificationConfirm}
                    onMarketingFormSubmit={onMarketingFormSubmit}
                    onStartCampaign={onStartCampaign}
                    onAcceptStageBProposal={onAcceptStageBProposal}
                    onAcceptStageCProposal={onAcceptStageCProposal}
                    onAcceptStageCScheduleProposal={onAcceptStageCScheduleProposal}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
