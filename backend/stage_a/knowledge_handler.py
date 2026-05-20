"""
Knowledge Handler Module
Handles complex questions that may need web search (Tavily) for accurate answers.
This is the "knowledge" intent path in the 3-way routing system.
"""

import json
from typing import Dict, Any, Generator, Optional, List
from rich import print as rprint

from .llm_provider import LLMProvider
from .tool_definitions import (
    GENERATE_SEARCH_QUERIES_TOOLS,
    build_messages_from_history
)
from .clarification import extract_first_json_block, normalize_tool_response
from .tavily_search import tavily_search_with_retry


def generate_search_queries(
    llm: LLMProvider,
    user_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    num_queries: int = 4,
) -> List[str]:
    """
    Generate 3-4 optimized search queries to comprehensively answer the user's question.
    
    Returns:
        List of search query strings
    """
    prompt = f"""Câu hỏi của người dùng: "{user_prompt}" """
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    system_msg = """Bạn là chuyên gia tạo câu tìm kiếm. Hãy tạo 3-4 câu tìm kiếm tối ưu (ngắn gọn, cụ thể, hiệu quả) để trả lời câu hỏi này."""
    
    raw = llm.generate(
        messages=messages,
        system_message=system_msg,
        tools=GENERATE_SEARCH_QUERIES_TOOLS,
        max_new_tokens=300
    )
    
    queries = []
    try:
        block = extract_first_json_block(raw)
        if block:
            parsed = json.loads(block)
            parsed = normalize_tool_response(parsed)
            queries = parsed.get("search_queries", [])
            # Fallback: nếu không đủ queries, thêm câu hỏi gốc
            if len(queries) < num_queries:
                queries.append(user_prompt)
    except (json.JSONDecodeError, KeyError):
        rprint("[yellow]⚠️ Query generation parse failed, using original prompt[/yellow]")
        queries = [user_prompt]
    
    # Giới hạn số lượng queries
    queries = queries[:num_queries]
    rprint(f"[cyan]🔎 Generated {len(queries)} search queries[/cyan]")
    
    return queries


def answer_with_search(
    llm: LLMProvider,
    user_prompt: str,
    search_results: list,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Generate a high-quality answer using search results as context.
    """
    # Format search results for the prompt
    sources_text = ""
    for i, result in enumerate(search_results, 1):
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("url", "")
        sources_text += f"\n[{i}] {title}\n    URL: {url}\n    Noi dung: {snippet}\n"

    prompt = f"""Cau hoi: "{user_prompt}"

Thong tin tim kiem duoc:
{sources_text}"""
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    system_msg = """Ban la tro ly AI thong minh. Hay tra loi cau hoi mot cach CHINH XAC va CHI TIET dua tren thong tin tim kiem.

Yeu cau:
Su dung thong tin tu nguon tim kiem de dam bao chinh xac
Neu co so lieu cu the, hay trich dan
Tra loi truc tiep
Chi tra ve noi dung tra loi, KHONG JSON"""
    
    answer = llm.generate(
        messages=messages,
        system_message=system_msg,
        max_new_tokens=1000
    )
    return answer.strip()


def answer_directly(
    llm: LLMProvider,
    user_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Generate a high-quality direct answer (no search needed).
    This produces more detailed responses than the simple chat path.
    """
    prompt = f"""Cau hoi: "{user_prompt}" """
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    system_msg = """Ban la tro ly AI thong minh va co kien thuc sau rong. Hay tra loi cau hoi mot cach CHI TIET, CHINH XAC va DE HIEU.

Yeu cau:
1. Tra loi bang tieng Viet
2. Giai thich ro rang, co cau truc
3. Neu can, dua ra vi du cu the
4. Chi tra ve noi dung tra loi, KHONG JSON"""
    
    answer = llm.generate(
        messages=messages,
        system_message=system_msg,
        max_new_tokens=600
    )
    return answer.strip()


def handle_knowledge_query(
    llm: LLMProvider,
    user_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Generator[Dict[str, Any], None, None]:
    """
    Main handler for the 'knowledge' intent path.
    Yields streaming events for the frontend.
    
    Flow:
    1. Generate 3-4 optimized search queries
    2. Execute searches for each query
    3. Aggregate results and answer with comprehensive context
    """
    rprint(f"[yellow][KNOWLEDGE] Processing: {user_prompt[:80]}...[/yellow]")

    # Step 1: Generate search queries
    yield {
        "status": "progress",
        "message": "Đang chuẩn bị các câu tìm kiếm..."
    }

    search_queries = generate_search_queries(llm, user_prompt, conversation_history, num_queries=4)
    
    if not search_queries:
        search_queries = [user_prompt]

    # Step 2: Execute searches for all queries
    all_search_results = []
    unique_urls = set()  # Track unique URLs to avoid duplicates

    for i, query in enumerate(search_queries, 1):
        yield {
            "status": "knowledge_searching",
            "message": f"🔍 Tìm kiếm ({i}/{len(search_queries)}): {query[:60]}..."
        }

        results = tavily_search_with_retry(
            query=query,
            max_results=5,
            freshness="year",
        )

        # Add only unique results
        for result in results:
            url = result.get("url", "")
            if url and url not in unique_urls:
                unique_urls.add(url)
                all_search_results.append(result)

        rprint(f"[cyan]Found {len(results)} results for query: {query}[/cyan]")

    # Step 3: Answer with aggregated search results
    yield {
        "status": "progress",
        "message": f"Tìm được {len(all_search_results)} nguồn. Đang phân tích..."
    }

    answer = answer_with_search(llm, user_prompt, all_search_results, conversation_history)

    # Format sources for frontend
    sources = [
        {
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("snippet", ""),
        }
        for r in all_search_results
        if r.get("url")
    ]

    yield {
        "status": "knowledge_response",
        "message": answer,
        "sources": sources,
    }

    rprint(f"[green]✅ Knowledge answer generated with {len(sources)} sources from {len(search_queries)} queries[/green]")
