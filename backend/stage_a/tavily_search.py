"""
Tavily Search Integration Module
Handles web search functionality with retry logic
"""

import json
import time
from typing import Any, Dict, List
from langchain_tavily import TavilySearch
from rich import print as rprint


def parse_tavily_result(raw: Any) -> List[Dict[str, Any]]:
    """Parse Tavily search result"""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []

    if isinstance(raw, dict):
        if raw.get("error"):
            print(f"Tavily error: {raw.get('error')}")
            return []
        raw = raw.get("results", [])

    if not isinstance(raw, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        
        row = {
            "title": str(item.get("title", "")).strip(),
            "url": str(item.get("url", "")).strip(),
            "snippet": str(item.get("content", item.get("snippet", ""))).strip(),
            "published_date": item.get("published_date") or item.get("publishedDate"),
        }
        
        if row["url"] or row["snippet"]:
            normalized.append(row)

    return normalized


def tavily_search_with_retry(
    query: str,
    max_results: int = 5,
    freshness: str = "year",
    retries: int = 3,
    sleep_sec: float = 1.5,
) -> List[Dict[str, Any]]:
    """
    Search with Tavily API with retry logic
    
    Args:
        query: Search query
        max_results: Max results per search (default 5)
        freshness: Time range filter (default "year")
        retries: Number of retry attempts
        sleep_sec: Sleep duration between retries
    
    Returns:
        List of search results
    """
    payload = {
        "query": query,
        "topic": "general",
        "search_depth": "advanced",
        "time_range": freshness,
    }

    tool = TavilySearch(max_results=max_results)
    last_error = None
    
    for attempt in range(1, retries + 1):
        try:
            result = tool.invoke(payload)
            parsed = parse_tavily_result(result)
            if parsed:
                rprint(f"[green]✅ Query succeeded: {query[:60]}... ({len(parsed)} results)[/green]")
                return parsed
        except Exception as ex:
            last_error = ex
            rprint(f"[yellow]Tavily attempt {attempt}/{retries} failed: {ex}[/yellow]")
        
        if attempt < retries:
            time.sleep(sleep_sec * attempt)

    rprint(f"[red]✗ Tavily failed after {retries} retries for: {query[:60]}...[/red]")
    return []


def initialize_tavily() -> TavilySearch:
    """Initialize and return Tavily search tool"""
    tool = TavilySearch(max_results=5)
    rprint("[green]✅ Tavily search tool initialized[/green]")
    return tool
