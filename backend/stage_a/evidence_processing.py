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


def normalize_and_filter_evidence(items: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Normalize and filter evidence items
    - Remove duplicates (URL and content-based)
    - Score sources
    - Sort by credibility
    
    Args:
        items: List of raw evidence items
    
    Returns:
        Cleaned and scored DataFrame
    """
    cleaned = []
    seen_urls = set()
    seen_signature = set()

    for item in items:
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        snippet = (item.get("snippet") or "").strip()

        # Skip if insufficient content
        if not url or len(snippet) < 40:
            continue

        # Duplicate detection
        key_url = url.lower().split("?")[0]
        signature = re.sub(r"\s+", " ", snippet.lower())[:180]

        if key_url in seen_urls or signature in seen_signature:
            continue

        seen_urls.add(key_url)
        seen_signature.add(signature)

        # Add normalized item
        cleaned.append({
            "title": title or "untitled",
            "url": url,
            "snippet": snippet,
            "published_date": item.get("published_date"),
            "source_score": score_source(url),
        })

    df = pd.DataFrame(cleaned)
    if not df.empty:
        df = df.sort_values(by=["source_score"], ascending=False).reset_index(drop=True)
    
    rprint(f"[green]✅ Evidence processed: {len(cleaned)} items from {len(items)} raw[/green]")
    return df


def get_top_evidence(df: pd.DataFrame, top_n: int = 20) -> List[Dict[str, Any]]:
    """Get top N evidence items"""
    return df.head(top_n).to_dict(orient='records')
