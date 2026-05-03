"""
Evidence Processing Module
Normalization, filtering, and source scoring
"""

import re
from typing import Any, Dict, List
import pandas as pd
from rich import print as rprint


TRUSTED_DOMAINS = {
    "statista.com": 0.9,
    "mordorintelligence.com": 0.75,
    "euromonitor.com": 0.85,
    "gov.vn": 0.95,
    "worldbank.org": 0.95,
    "oecd.org": 0.95,
    "forbes.com": 0.7,
}


def score_source(url: str) -> float:
    """Score source credibility based on domain"""
    lowered = (url or "").lower()
    
    for domain, score in TRUSTED_DOMAINS.items():
        if domain in lowered:
            return score
    
    if lowered.startswith("http"):
        return 0.6
    
    return 0.2


def calculate_relevance_score(snippet: str, query_keywords: List[str] = None) -> float:
    """
    Calculate relevance score based on keyword presence
    
    Args:
        snippet: Text snippet to score
        query_keywords: Optional list of keywords to match
    
    Returns:
        Relevance score 0.0-1.0
    """
    if not snippet:
        return 0.0
    
    # Base score: snippet length and quality (longer = more detailed)
    length_score = min(len(snippet) / 500, 1.0)  # Max at 500 chars
    
    # Bonus for having numbers (statistics)
    has_numbers = bool(re.search(r'\d+[.,]\d+|\d{3,}', snippet))
    number_bonus = 0.2 if has_numbers else 0.0
    
    # Bonus for keywords if provided
    keyword_bonus = 0.0
    if query_keywords:
        keyword_matches = sum(1 for kw in query_keywords if kw.lower() in snippet.lower())
        keyword_bonus = min(keyword_matches / len(query_keywords), 0.3) if query_keywords else 0.0
    
    return min(length_score + number_bonus + keyword_bonus, 1.0)


def normalize_and_filter_evidence(
    items: List[Dict[str, Any]],
    min_quality_score: float = 0.5,
    max_items: int = 15
) -> pd.DataFrame:
    """
    Normalize and filter evidence items with strict quality control
    - Remove duplicates (URL and content-based)
    - Score sources and relevance
    - Filter by quality threshold
    - Limit total items to prevent out-of-memory
    
    Args:
        items: List of raw evidence items
        min_quality_score: Minimum combined score to keep (0.0-1.0)
        max_items: Maximum items to return (default 15)
    
    Returns:
        Cleaned and scored DataFrame (sorted by quality)
    """
    cleaned = []
    seen_urls = set()
    seen_signature = set()

    for item in items:
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        snippet = (item.get("snippet") or "").strip()

        # Skip if insufficient content
        if not url or len(snippet) < 50:
            continue

        # Duplicate detection
        key_url = url.lower().split("?")[0]
        signature = re.sub(r"\s+", " ", snippet.lower())[:180]

        if key_url in seen_urls or signature in seen_signature:
            continue

        seen_urls.add(key_url)
        seen_signature.add(signature)

        # Calculate quality scores
        source_score = score_source(url)
        relevance_score = calculate_relevance_score(snippet)
        combined_score = (source_score * 0.6 + relevance_score * 0.4)

        # Skip items below quality threshold
        if combined_score < min_quality_score:
            rprint(f"[dim]⊘ Skipped low-quality: {title[:50]} (score={combined_score:.2f})[/dim]")
            continue

        # Add normalized item
        cleaned.append({
            "title": title or "untitled",
            "url": url,
            "snippet": snippet,
            "published_date": item.get("published_date"),
            "source_score": source_score,
            "relevance_score": relevance_score,
            "combined_score": combined_score,
        })

    # Sort by combined score and limit to max_items
    df = pd.DataFrame(cleaned)
    if not df.empty:
        df = df.sort_values(by=["combined_score"], ascending=False).reset_index(drop=True)
        df = df.head(max_items)
    
    rprint(f"[green]✅ Evidence processed: {len(df)} items (kept from {len(cleaned)}, raw {len(items)})[/green]")
    rprint(f"[yellow]Quality threshold: {min_quality_score:.2f} | Max items: {max_items}[/yellow]")
    return df


def get_top_evidence(df: pd.DataFrame, top_n: int = 20) -> List[Dict[str, Any]]:
    """Get top N evidence items"""
    return df.head(top_n).to_dict(orient='records')
