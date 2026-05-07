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


def extract_first_json_block(text: str) -> Optional[str]:
    """Extract first JSON object or array from text"""
    if not text:
        return None
    
    match_obj = re.search(r"\{[\s\S]*\}", text)
    if match_obj:
        return match_obj.group(0)
    
    match_arr = re.search(r"\[[\s\S]*\]", text)
    if match_arr:
        return match_arr.group(0)
    
    return None


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
- nganh_hang: {partial_input.nganh_hang if partial_input.nganh_hang else '(CHUA CO)'}
- thi_truong_muc_tieu: {partial_input.thi_truong_muc_tieu if partial_input.thi_truong_muc_tieu else '(CHUA CO)'}
- phan_khuc_quan_tam: {partial_input.phan_khuc_quan_tam if partial_input.phan_khuc_quan_tam else '(CHUA CO)'}
- doi_thu_seed: {partial_input.doi_thu_seed if partial_input.doi_thu_seed else '(CHUA CO)'}
- khung_thoi_gian: {partial_input.khung_thoi_gian if partial_input.khung_thoi_gian else '(CHUA CO)'}
- muc_tieu_nghien_cuu: {partial_input.muc_tieu_nghien_cuu if partial_input.muc_tieu_nghien_cuu else '(CHUA CO)'}"""
    
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
            "nganh_hang": partial_input.nganh_hang or "",
            "thi_truong_muc_tieu": partial_input.thi_truong_muc_tieu or "",
            "phan_khuc_quan_tam": partial_input.phan_khuc_quan_tam or [],
            "doi_thu_seed": partial_input.doi_thu_seed or [],
            "muc_tieu_nghien_cuu": partial_input.muc_tieu_nghien_cuu or []
        },
        "explanations": {},
        "ready_to_proceed": validation_result.get("completeness_score", 50) >= 70,
    }
    
    if block:
        try:
            parsed = json.loads(block)
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
        nganh_hang=(
            user_responses.get("nganh_hang") if user_responses
            else request["suggested_values"].get("nganh_hang", "")
        ),
        thi_truong_muc_tieu=(
            user_responses.get("thi_truong_muc_tieu") if user_responses
            else request["suggested_values"].get("thi_truong_muc_tieu", "")
        ),
        phan_khuc_quan_tam=(
            user_responses.get("phan_khuc_quan_tam") if user_responses
            else request["suggested_values"].get("phan_khuc_quan_tam", [])
        ),
        doi_thu_seed=(
            user_responses.get("doi_thu_seed") if user_responses
            else request["suggested_values"].get("doi_thu_seed", [])
        ),
        khung_thoi_gian=partial_input.khung_thoi_gian,
        muc_tieu_nghien_cuu=(
            user_responses.get("muc_tieu_nghien_cuu") if user_responses
            else request["suggested_values"].get("muc_tieu_nghien_cuu", [])
        ),
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
