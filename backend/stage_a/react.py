"""
ReAct Agent Loop Module
Reasoning + Acting loop for intelligent search planning
"""

import json
from typing import Any, Dict, List, Optional
from rich import print as rprint

from .llm_provider import LLMProvider
from .tool_definitions import (
    REACT_TOOLS,
    SYSTEM_MESSAGE_REACT_DECIDER,
    build_messages_from_history
)
from .clarification import extract_first_json_block
from .tavily_search import tavily_search_with_retry


def react_decide_action(
    llm: LLMProvider,
    step: str,
    collected_evidence_count: int,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    ReAct controller decides next action
    
    Returns:
        - action: "search" | "refine_query" | "summarize"
        - query: Search query or statement
        - reason: Reasoning for action
    """
    prompt = f"""Nhiem vu hien tai: {step}
So bang chung da co: {collected_evidence_count}"""
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    raw = llm.generate(
        messages=messages,
        system_message=SYSTEM_MESSAGE_REACT_DECIDER,
        tools=REACT_TOOLS,
        max_new_tokens=220
    )
    block = extract_first_json_block(raw)
    
    if block:
        try:
            decision = json.loads(block)
            action = decision.get("action", "search")
            if action not in {"search", "refine_query", "summarize"}:
                action = "search"
            return {
                "action": action,
                "query": decision.get("query", step),
                "reason": decision.get("reason", ""),
            }
        except json.JSONDecodeError:
            pass
    
    return {"action": "search", "query": step, "reason": "fallback"}


def run_react_loop(
    llm: LLMProvider,
    plan: Dict[str, Any],
    conversation_history: Optional[List[Dict[str, str]]] = None,
    max_tool_calls: int = 14
) -> Dict[str, Any]:
    """
    Run ReAct loop with search steps
    
    Args:
        llm: LLM provider instance
        plan: Plan with search steps
        conversation_history: Previous conversation messages
        max_tool_calls: Max search calls
    
    Returns:
        Dict with evidence and intermediate steps
    """
    steps = plan.get("steps", [])
    evidence: List[Dict[str, Any]] = []
    intermediate_steps: List[Dict[str, Any]] = []
    tool_calls = 0

    rprint(f"[yellow]Starting ReAct loop with {len(steps)} steps...[/yellow]")

    for step_idx, step in enumerate(steps, start=1):
        if tool_calls >= max_tool_calls:
            break

        # Decide action
        decision = react_decide_action(llm, step, len(evidence), conversation_history)
        # Ensure query is a string (step might be dict or string)
        query_raw = decision.get("query") or step
        query = str(query_raw).strip() if query_raw else ""
        action = decision.get("action", "search")

        # Skip summarize action (no tool call)
        if action == "summarize":
            intermediate_steps.append({
                "step": step_idx,
                "action": action,
                "query": query,
                "result_count": 0,
                "note": "summarize - skipped tool call",
            })
            continue

        # Refine query if needed
        if action == "refine_query":
            query = f"{query} {step}".strip()

        # Execute search
        results = tavily_search_with_retry(query=query, max_results=5, freshness="year")
        tool_calls += 1

        intermediate_steps.append({
            "step": step_idx,
            "action": action,
            "query": query,
            "result_count": len(results),
            "reason": decision.get("reason", ""),
        })
        evidence.extend(results)

    rprint(f"[green]✅ ReAct loop completed: {tool_calls} tool calls, {len(evidence)} evidence items[/green]")

    return {
        "evidence": evidence,
        "intermediate_steps": intermediate_steps,
        "tool_calls": tool_calls,
    }
