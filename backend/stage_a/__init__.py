"""
Stage A Market Research Agent Package
Local LLM-based pipeline: Planning -> ReAct -> Tool Use
"""

from .data_models import StageAInput, EvidenceItem, StageAOutput
from .llm_config import LocalLLMConfig, LocalTextGenerator
from .environment import load_environment, setup_directories
from .clarification import (
    validate_input_completeness,
    request_additional_information,
    clarify_user_prompt,
)
from .planning import planner_chain
from .tavily_search import initialize_tavily, tavily_search_with_retry, parse_tavily_result
from .react import react_decide_action, run_react_loop
from .evidence_processing import normalize_and_filter_evidence, score_source
from .synthesis import (
    synthesize_tong_quan_thi_truong,
    synthesize_phan_tich_doi_thu,
    synthesize_xu_huong_nganh,
    synthesize_phan_khuc_va_insight,
    synthesize_stage_a_report,
)
from .output_formatting import build_markdown_report, convert_evidence_to_dict
from .mongodb import MongoDBManager
from .flask_api import app
from .ngrok_tunnel import setup_ngrok_tunnel, run_server

__version__ = "1.0.0"
__all__ = [
    "StageAInput",
    "EvidenceItem",
    "StageAOutput",
    "LocalLLMConfig",
    "LocalTextGenerator",
    "load_environment",
    "setup_directories",
    "validate_input_completeness",
    "request_additional_information",
    "clarify_user_prompt",
    "planner_chain",
    "initialize_tavily",
    "tavily_search_with_retry",
    "parse_tavily_result",
    "react_decide_action",
    "run_react_loop",
    "normalize_and_filter_evidence",
    "score_source",
    "synthesize_tong_quan_thi_truong",
    "synthesize_phan_tich_doi_thu",
    "synthesize_xu_huong_nganh",
    "synthesize_phan_khuc_va_insight",
    "synthesize_stage_a_report",
    "build_markdown_report",
    "convert_evidence_to_dict",
    "MongoDBManager",
    "app",
    "setup_ngrok_tunnel",
    "run_server",
]
