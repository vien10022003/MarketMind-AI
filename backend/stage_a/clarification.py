"""
Clarification Module - 2-Step Validation
LLM-based clarification of user input with validation and suggestions
"""

import json
import re
from typing import Any, Dict, Optional, List
from rich import print as rprint

from .data_models import StageAInput
from .llm_provider import LLMProvider
from .tool_definitions import (
    INPUT_VALIDATION_TOOLS,
    CLARIFICATION_TOOLS,
    SYSTEM_MESSAGE_INPUT_VALIDATOR,
    build_messages_from_history
)


def normalize_tool_response(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize tool calling response format to direct response format.
    
    Handles both:
    - Direct format: {"key": "value", ...}
    - Tool format: {"name": "tool_name", "parameters": {"key": "value", ...}}
    
    Returns the normalized parameters dict.
    """
    # If response has "parameters" key (tool calling format), extract it
    if "parameters" in parsed and isinstance(parsed["parameters"], dict):
        return parsed["parameters"]
    # Otherwise return as-is (direct format)
    return parsed


def extract_first_json_block(text: str) -> Optional[str]:
    """Extract first JSON object or array from text with proper bracket matching"""
    if not text:
        return None
    
    # Try to find first { or [ and match it properly
    start_idx = -1
    is_array = False
    
    # Find first { or [
    brace_idx = text.find('{')
    bracket_idx = text.find('[')
    
    if brace_idx == -1 and bracket_idx == -1:
        return None
    elif brace_idx == -1:
        start_idx = bracket_idx
        is_array = True
    elif bracket_idx == -1:
        start_idx = brace_idx
        is_array = False
    else:
        if brace_idx < bracket_idx:
            start_idx = brace_idx
            is_array = False
        else:
            start_idx = bracket_idx
            is_array = True
    
    # Match braces/brackets respecting string boundaries
    open_char = '[' if is_array else '{'
    close_char = ']' if is_array else '}'
    
    depth = 0
    in_string = False
    escape_next = False
    end_idx = -1
    
    for i in range(start_idx, len(text)):
        char = text[i]
        
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not in_string:
            in_string = True
            continue
        elif char == '"' and in_string:
            in_string = False
            continue
        
        if not in_string:
            if char == open_char:
                depth += 1
            elif char == close_char:
                depth -= 1
                if depth == 0:
                    end_idx = i + 1
                    break
    
    if end_idx == -1:
        return None
    
    extracted = text[start_idx:end_idx]
    
    # Clean up common invalid escape sequences before parsing
    # Replace \' with ' since JSON doesn't support escaping single quotes
    cleaned = extracted.replace("\\'", "'")
    
    return cleaned


def validate_input_completeness(
    llm: LLMProvider,
    user_prompt: str,
    partial_input: StageAInput,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    STEP 1: LLM validates what info is present and missing
    
    Returns:
    - missing_fields: {field_name: {importance, reason}}
    - completeness_score: 0-100
    - can_proceed_with_suggestions: bool
    """
    prompt = f"""User prompt (chi tieu hang): "{user_prompt}"

Thong tin hien co:
- ban_chat_san_pham: {partial_input.ban_chat_san_pham if partial_input.ban_chat_san_pham else '(CHUA CO)'}
- khach_hang_muc_tieu: {partial_input.khach_hang_muc_tieu if partial_input.khach_hang_muc_tieu else '(CHUA CO)'}
- gia_tri_cot_loi: {partial_input.gia_tri_cot_loi if partial_input.gia_tri_cot_loi else '(CHUA CO)'}
- gia_ca_chinh_sach: {partial_input.gia_ca_chinh_sach if partial_input.gia_ca_chinh_sach else '(CHUA CO)'}"""
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    raw = llm.generate(
        messages=messages,
        system_message=SYSTEM_MESSAGE_INPUT_VALIDATOR,
        tools=INPUT_VALIDATION_TOOLS,
        max_new_tokens=400
    )
    block = extract_first_json_block(raw)
    
    result = {
        "missing_fields": {},
        "can_infer_from_prompt": {},
        "completeness_score": 50,
        "can_proceed_with_suggestions": False,
        "notes": ""
    }
    
    if block:
        try:
            parsed = json.loads(block)
            # Normalize tool calling response format
            parsed = normalize_tool_response(parsed)
            result.update(parsed)
            rprint("[green]✅ Validation completed[/green]")
            rprint(f"  Completeness: {parsed.get('completeness_score', 0)}%")
            rprint(f"  Missing fields: {list(parsed.get('missing_fields', {}).keys())}")
        except json.JSONDecodeError:
            rprint("[yellow]⚠️ Validation JSON parse failed[/yellow]")
    
    return result


def request_additional_information(
    llm: LLMProvider,
    user_prompt: str,
    partial_input: StageAInput,
    validation_result: Dict[str, Any],
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    STEP 2: LLM generates questions and suggestions based on validation
    
    Returns:
    - questions_to_ask: List of questions
    - suggested_values: Suggested field values
    - explanations: Why those values were chosen
    - ready_to_proceed: bool
    """
    missing_info = validation_result.get("missing_fields", {})
    
    missing_list = []
    for field, details in missing_info.items():
        if details.get("importance") in ["high", "medium"]:
            missing_list.append(f"- {field}: {details.get('reason', '')}")
    
    prompt = f"""User prompt: "{user_prompt}"

Completeness: {validation_result.get('completeness_score', 0)}%
Missing (high+medium): {missing_list if missing_list else 'Khong co'}"""
    
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    
    raw = llm.generate(
        messages=messages,
        system_message="Ban la AI consultant huong dan user cap them thong tin chi tiet. Tao cau hoi SPECIFIC va SUGGEST gia tri.",
        tools=CLARIFICATION_TOOLS,
        max_new_tokens=500
    )
    block = extract_first_json_block(raw)
    
    result = {
        "has_critical_gaps": len(missing_list) > 0,
        "questions_to_ask": [],
        "suggested_values": {
            "ban_chat_san_pham": partial_input.ban_chat_san_pham or "",
            "khach_hang_muc_tieu": partial_input.khach_hang_muc_tieu or "",
            "gia_tri_cot_loi": partial_input.gia_tri_cot_loi or "",
            "gia_ca_chinh_sach": partial_input.gia_ca_chinh_sach or ""
        },
        "explanations": {},
        "ready_to_proceed": validation_result.get("completeness_score", 50) >= 70,
    }
    
    if block:
        try:
            parsed = json.loads(block)
            # Normalize tool calling response format
            parsed = normalize_tool_response(parsed)
            result.update(parsed)
            rprint("[green]✅ Suggestions generated[/green]")
        except json.JSONDecodeError:
            rprint("[yellow]⚠️ Suggestions JSON parse failed[/yellow]")
    
    return result


def clarify_user_prompt(
    llm: LLMProvider,
    user_prompt: str,
    partial_input: StageAInput,
    user_responses: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    2-Step clarification workflow:
    1. Validate - check what info is present/missing
    2. Request - generate questions and suggestions
    
    Returns refined StageAInput and clarification status
    """
    rprint("[yellow]Step 1: Validating input...[/yellow]")
    validation = validate_input_completeness(llm, user_prompt, partial_input, conversation_history)
    
    rprint("[yellow]Step 2: Generating suggestions...[/yellow]")
    request = request_additional_information(llm, user_prompt, partial_input, validation, conversation_history)
    
    # Merge user responses or use suggestions
    final_input = StageAInput(
        user_prompt=user_prompt,
        ban_chat_san_pham=(
            user_responses.get("ban_chat_san_pham") if user_responses
            else request["suggested_values"].get("ban_chat_san_pham", "")
        ),
        khach_hang_muc_tieu=(
            user_responses.get("khach_hang_muc_tieu") if user_responses
            else request["suggested_values"].get("khach_hang_muc_tieu", "")
        ),
        gia_tri_cot_loi=(
            user_responses.get("gia_tri_cot_loi") if user_responses
            else request["suggested_values"].get("gia_tri_cot_loi", "")
        ),
        gia_ca_chinh_sach=(
            user_responses.get("gia_ca_chinh_sach") if user_responses
            else request["suggested_values"].get("gia_ca_chinh_sach", "")
        )
    )
    
    has_questions = len(request.get("questions_to_ask", [])) > 0 and not user_responses
    
    return {
        "step": "waiting_for_input" if has_questions else "completed",
        "validation": validation,
        "request": request,
        "clarified_input": final_input,
        "questions": request.get("questions_to_ask", []),
        "suggestions": request.get("suggested_values", {}),
        "explanations": request.get("explanations", {}),
        "ready_to_proceed": request.get("ready_to_proceed", False),
    }
