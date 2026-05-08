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
    KNOWLEDGE_SEARCH_DECISION_TOOLS,
    build_messages_from_history
)
from .clarification import extract_first_json_block, normalize_tool_response
from .tavily_search import tavily_search_with_retry


def assess_need_for_search(
    llm: LLMProvider,
    user_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """
    LLM evaluates whether the question requires a web search for an accurate answer.
    
    Returns:
        {
            "needs_search": True/False,
            "search_query": "optimized search query" (if needs_search),
            "reasoning": "why search is needed or not"
        }
    """
    prompt = f"""Cau hoi nguoi dung: "{user_prompt}" """
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    system_msg = """Ban la he thong danh gia cau hoi. Nhiem vu: xac dinh xem cau hoi co CAN TIM KIEM TREN INTERNET de tra loi chinh xac hay khong.

CAN tim kiem khi:
- Hoi ve du kien cu the, con so, thong ke
- Hoi ve su kien, tin tuc moi nhat
- Hoi ve san pham, cong ty, thuong hieu cu the
- Hoi ve thong tin co the thay doi theo thoi gian

KHONG can tim kiem khi:
- Giai thich khai niem chung
- Cau hoi ve ly thuyet, nguyen ly co ban
- So sanh tong quat giua cac khai niem"""
    
    raw = llm.generate(
        messages=messages,
        system_message=system_msg,
        tools=KNOWLEDGE_SEARCH_DECISION_TOOLS,
        max_new_tokens=250
    )
    block = extract_first_json_block(raw)

    result = {
        "needs_search": False,
        "search_query": "",
        "reasoning": "default - no search"
    }

    if block:
        try:
            parsed = json.loads(block)
            # Normalize tool calling response format
            parsed = normalize_tool_response(parsed)
            result.update(parsed)
            # Ensure boolean type
            result["needs_search"] = bool(result.get("needs_search", False))
            rprint(f"[cyan]🔎 Search assessment: needs_search={result['needs_search']} — {result['reasoning']}[/cyan]")
        except json.JSONDecodeError:
            rprint("[yellow]⚠️ Search assessment parse failed, defaulting to no search[/yellow]")

    return result


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
    1. Assess if search is needed
    2. If yes → Tavily search → answer with context
    3. If no → answer directly with LLM knowledge
    """
    rprint(f"[yellow][KNOWLEDGE] Processing: {user_prompt[:80]}...[/yellow]")

    # Step 1: Assess need for search
    yield {
        "status": "progress",
        "message": "Đang đánh giá câu hỏi..."
    }

    assessment = assess_need_for_search(llm, user_prompt, conversation_history)

    if assessment["needs_search"]:
        # Step 2a: Search with Tavily
        search_query = assessment.get("search_query", user_prompt)
        rprint(f"[yellow][KNOWLEDGE] Searching: {search_query}[/yellow]")

        yield {
            "status": "knowledge_searching",
            "message": f"🔍 Đang tìm kiếm thông tin: {search_query[:80]}..."
        }

        search_results = tavily_search_with_retry(
            query=search_query,
            max_results=5,
            freshness="year",
        )

        # Step 3a: Answer with search results
        yield {
            "status": "progress",
            "message": f"Tìm được {len(search_results)} nguồn. Đang phân tích..."
        }

        answer = answer_with_search(llm, user_prompt, search_results, conversation_history)

        # Format sources for frontend
        sources = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("snippet", ""),
            }
            for r in search_results
            if r.get("url")
        ]

        yield {
            "status": "knowledge_response",
            "message": answer,
            "sources": sources,
        }

        rprint(f"[green]✅ Knowledge answer generated with {len(sources)} sources[/green]")

    else:
        # Step 2b: Answer directly
        rprint(f"[yellow][KNOWLEDGE] Answering directly (no search needed)[/yellow]")

        yield {
            "status": "progress",
            "message": "Đang suy nghĩ câu trả lời..."
        }

        answer = answer_directly(llm, user_prompt, conversation_history)

        yield {
            "status": "knowledge_response",
            "message": answer,
            "sources": [],
        }

        rprint(f"[green]✅ Knowledge answer generated (direct, no search)[/green]")
