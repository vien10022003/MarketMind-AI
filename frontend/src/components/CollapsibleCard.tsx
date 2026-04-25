import { useState, useRef, useEffect, type ReactNode } from 'react';

interface CollapsibleCardProps {
  title: string;
  summary: string;
  icon: string;
  children: ReactNode;
  defaultOpen?: boolean;
  accentColor?: string;
}

export function CollapsibleCard({
  title,
  summary,
  icon,
  children,
  defaultOpen = false,
  accentColor = 'var(--primary-color)',
}: CollapsibleCardProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentHeight, setContentHeight] = useState(0);

  useEffect(() => {
    if (contentRef.current) {
      setContentHeight(contentRef.current.scrollHeight);
    }
  }, [isOpen, children]);

  return (
    <div className={`collapsible-card ${isOpen ? 'is-open' : ''}`} style={{ '--accent': accentColor } as React.CSSProperties}>
      <button
        className="collapsible-header"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span className="collapsible-icon">{icon}</span>
        <div className="collapsible-info">
          <span className="collapsible-title">{title}</span>
          <span className="collapsible-summary">{summary}</span>
        </div>
        <span className={`collapsible-chevron ${isOpen ? 'rotated' : ''}`}>
          ▾
        </span>
      </button>

      <div
        className="collapsible-body"
        style={{ maxHeight: isOpen ? `${contentHeight}px` : '0px' }}
      >
        <div ref={contentRef} className="collapsible-inner">
          {children}
        </div>
      </div>
    </div>
  );
}
