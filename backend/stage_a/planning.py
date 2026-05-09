"""
Planning Module
Planner chain that generates research questions and search steps
"""

import json
import re
from typing import Any, Dict, Optional, List
from rich import print as rprint

from .data_models import StageAInput
from .llm_provider import LLMProvider
from .tool_definitions import (
    PLANNING_TOOLS,
    SYSTEM_MESSAGE_PLANNER,
    build_messages_from_history
)
from .clarification import extract_first_json_block, normalize_tool_response


def planner_chain(
    llm: LLMProvider,
    research_input: StageAInput,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    max_steps: int = 8
) -> Dict[str, Any]:
    """
    Generate research plan with questions and search steps
    
    Args:
        llm: LLM provider instance
        research_input: StageAInput configuration
        conversation_history: Previous conversation messages
        max_steps: Max number of search steps
    
    Returns:
        Dict with research_questions, hypotheses, steps, success_criteria
    """
    prompt = f"""Input:
- nganh_hang: {research_input.nganh_hang}
- thi_truong_muc_tieu: {research_input.thi_truong_muc_tieu}
- phan_khuc_quan_tam: {research_input.phan_khuc_quan_tam}
- doi_thu_seed: {research_input.doi_thu_seed}
- khung_thoi_gian: {research_input.khung_thoi_gian}
- muc_tieu_nghien_cuu: {research_input.muc_tieu_nghien_cuu}"""
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    raw = llm.generate(
        messages=messages,
        system_message=SYSTEM_MESSAGE_PLANNER,
        tools=PLANNING_TOOLS,
        max_new_tokens=1200
    )
    rprint(f"[blue]Raw output:[/blue] {raw}")
    block = extract_first_json_block(raw)
    rprint(f"[blue]block:[/blue] {block}")

    if block:
        try:
            plan = json.loads(block)
            # Normalize tool calling response format
            plan = normalize_tool_response(plan)
            
            # Handle stringified JSON arrays in plan fields
            for key in ['research_questions', 'hypotheses']:
                if key in plan and isinstance(plan[key], str):
                    try:
                        plan[key] = json.loads(plan[key])
                    except json.JSONDecodeError:
                        # Keep as string if can't parse
                        pass
            
            plan["steps"] = plan.get("steps", [])[:max_steps]
            rprint("[green]✅ Planning completed[/green]")
            rprint(f"  Steps: {len(plan.get('steps', []))} search queries")
            return plan
        except json.JSONDecodeError:
            rprint("[red]✗ Failed to parse JSON from planner output[/red]")
            pass

    # Fallback plan
    rprint("[yellow]⚠️ Using fallback plan[/yellow]")
    fallback_steps = [
        f"Quy mo va toc do tang truong thi truong {research_input.nganh_hang} tai {research_input.thi_truong_muc_tieu} {research_input.khung_thoi_gian}",
        f"Top doi thu cua {research_input.nganh_hang} tai {research_input.thi_truong_muc_tieu} va dinh vi san pham",
        f"Xu huong tieu dung {research_input.nganh_hang} tai {research_input.thi_truong_muc_tieu} {research_input.khung_thoi_gian}",
        f"Insight hanh vi mua cua cac phan khuc {', '.join(research_input.phan_khuc_quan_tam or ['khach hang muc_tieu'])}",
    ][:max_steps]
    
    return {
        "research_questions": research_input.muc_tieu_nghien_cuu or ["Market research"],
        "hypotheses": ["Nguoi dung uu tien san pham an toan, minh bach thanh phan, gia hop ly"],
        "steps": fallback_steps,
        "success_criteria": ["Moi deliverable co citation URL ro rang"],
    }
