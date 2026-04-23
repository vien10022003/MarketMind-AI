"""
Planning Module
Planner chain that generates research questions and search steps
"""

import json
import re
from typing import Any, Dict, Optional
from rich import print as rprint

from .04_data_models import StageAInput
from .03_llm_config import LocalTextGenerator
from .05_clarification import extract_first_json_block


def planner_chain(
    llm: LocalTextGenerator,
    research_input: StageAInput,
    max_steps: int = 8
) -> Dict[str, Any]:
    """
    Generate research plan with questions and search steps
    
    Args:
        llm: LocalTextGenerator instance
        research_input: StageAInput configuration
        max_steps: Max number of search steps
    
    Returns:
        Dict with research_questions, hypotheses, steps, success_criteria
    """
    prompt = f"""
Ban la Planner cho Stage A marketing research.
Hay tao ke hoach thu thap bang chung machine-readable JSON, KHONG ghi giai thich ngoai JSON.

Yeu cau:
1) Tao 5-8 cau hoi nghien cuu.
2) Tao danh sach steps (moi step la 1 truy van web_search cu the).
3) Steps phai huong den 4 deliverables:
   - tong quan thi truong
   - phan tich doi thu
   - xu huong nganh
   - phan khuc va insight khach hang

Input:
- nganh_hang: {research_input.nganh_hang}
- thi_truong_muc_tieu: {research_input.thi_truong_muc_tieu}
- phan_khuc_quan_tam: {research_input.phan_khuc_quan_tam}
- doi_thu_seed: {research_input.doi_thu_seed}
- khung_thoi_gian: {research_input.khung_thoi_gian}
- muc_tieu_nghien_cuu: {research_input.muc_tieu_nghien_cuu}

JSON schema:
{{
  "research_questions": ["...", "..."],
  "hypotheses": ["...", "..."],
  "steps": ["web search query 1", "web search query 2"],
  "success_criteria": ["..."]
}}
"""
    raw = llm.generate(prompt, max_new_tokens=900)
    block = extract_first_json_block(raw)

    if block:
        try:
            plan = json.loads(block)
            plan["steps"] = plan.get("steps", [])[:max_steps]
            rprint("[green]✅ Planning completed[/green]")
            rprint(f"  Steps: {len(plan.get('steps', []))} search queries")
            return plan
        except json.JSONDecodeError:
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
