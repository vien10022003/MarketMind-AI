/**
 * Simple Markdown to JSX parser
 * Handles: bold, headings, lists, line breaks, etc.
 */

export interface ParsedContent {
  type: 'text' | 'bold' | 'heading1' | 'heading2' | 'heading3' | 'list' | 'paragraph' | 'br';
  content?: string | ParsedContent[] | string[];
  level?: number;
}

/**
 * Parse markdown text into structured content
 */
export function parseMarkdown(text: string): ParsedContent[] {
  if (!text) return [];

  const lines = text.split('\n');
  const result: ParsedContent[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Skip empty lines but keep one blank
    if (!line.trim()) {
      if (result.length > 0 && result[result.length - 1].type !== 'br') {
        result.push({ type: 'br' });
      }
      i++;
      continue;
    }

    // Heading 1: # title
    if (line.match(/^#\s+/)) {
      result.push({
        type: 'heading1',
        content: line.replace(/^#\s+/, '').trim(),
      });
      i++;
      continue;
    }

    // Heading 2: ## title
    if (line.match(/^##\s+/)) {
      result.push({
        type: 'heading2',
        content: line.replace(/^##\s+/, '').trim(),
      });
      i++;
      continue;
    }

    // Heading 3: ### title
    if (line.match(/^###\s+/)) {
      result.push({
        type: 'heading3',
        content: line.replace(/^###\s+/, '').trim(),
      });
      i++;
      continue;
    }

    // List items: - item or * item
    if (line.match(/^\s*[-*]\s+/)) {
      const listItems: string[] = [];
      while (i < lines.length && lines[i].match(/^\s*[-*]\s+/)) {
        listItems.push(lines[i].replace(/^\s*[-*]\s+/, '').trim());
        i++;
      }
      result.push({
        type: 'list',
        content: listItems,
      });
      continue;
    }

    // Regular paragraph (may contain bold)
    result.push({
      type: 'paragraph',
      content: parseBold(line),
    });
    i++;
  }

  return result;
}

/**
 * Parse bold text: **text** or __text__
 */
function parseBold(text: string): ParsedContent[] {
  const result: ParsedContent[] = [];
  const regex = /\*\*(.*?)\*\*|__(.*?)__/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    // Add text before match
    if (match.index > lastIndex) {
      result.push({
        type: 'text',
        content: text.substring(lastIndex, match.index),
      });
    }

    // Add bold text
    result.push({
      type: 'bold',
      content: match[1] || match[2],
    });

    lastIndex = regex.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    result.push({
      type: 'text',
      content: text.substring(lastIndex),
    });
  }

  return result.length > 0
    ? result
    : [{ type: 'text', content: text }];
}

/**
 * Convert parsed markdown to React JSX
 */
export function renderMarkdown(parsed: ParsedContent[]): React.ReactNode {
  return parsed.map((item, idx) => {
    switch (item.type) {
      case 'heading1':
        return (
          <h2 key={idx} className="markdown-h1">
            {String(item.content || '')}
          </h2>
        );
      case 'heading2':
        return (
          <h3 key={idx} className="markdown-h2">
            {String(item.content || '')}
          </h3>
        );
      case 'heading3':
        return (
          <h4 key={idx} className="markdown-h3">
            {String(item.content || '')}
          </h4>
        );
      case 'list':
        return (
          <ul key={idx} className="markdown-list">
            {(item.content as unknown as string[]).map((listItem, i) => (
              <li key={i}>{renderBoldText(String(listItem || ''))}</li>
            ))}
          </ul>
        );
      case 'paragraph':
        return (
          <p key={idx} className="markdown-paragraph">
            {renderBoldContent(item.content as ParsedContent[])}
          </p>
        );
      case 'br':
        return <div key={idx} className="markdown-break" />;
      default:
        return null;
    }
  });
}

/**
 * Render bold inline content
 */
function renderBoldContent(content: ParsedContent[]): React.ReactNode {
  if (!Array.isArray(content)) {
    return <span>{String(content || '')}</span>;
  }
  return content.map((item, idx) => {
    if (item.type === 'bold') {
      return (
        <strong key={idx} className="markdown-bold">
          {String(item.content || '')}
        </strong>
      );
    }
    if (item.type === 'text') {
      return <span key={idx}>{String(item.content || '')}</span>;
    }
    return <span key={idx}>{String(item.content || '')}</span>;
  });
}

/**
 * Helper to render bold in list items
 */
function renderBoldText(text: string): React.ReactNode {
  if (!text) return null;
  const parts = text.split(/(\*\*.*?\*\*|__.*?__)/);
  const elements = parts
    .filter(part => part.length > 0)
    .map((part, idx) => {
      if (part.match(/^\*\*.*\*\*$/) || part.match(/^__.*__$/)) {
        return (
          <strong key={idx} className="markdown-bold">
            {part.replace(/^\*\*|\*\*$|^__|__$/g, '')}
          </strong>
        );
      }
      return <span key={idx}>{part}</span>;
    });
  return elements.length > 0 ? elements : null;
}
