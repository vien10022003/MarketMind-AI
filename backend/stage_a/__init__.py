"""
Stage A Market Research Agent Package
Local LLM-based pipeline: Planning -> ReAct -> Tool Use
"""

from .04_data_models import StageAInput, EvidenceItem, StageAOutput
from .03_llm_config import LocalLLMConfig, LocalTextGenerator

__version__ = "1.0.0"
__all__ = [
    "StageAInput",
    "EvidenceItem",
    "StageAOutput",
    "LocalLLMConfig",
    "LocalTextGenerator",
]
