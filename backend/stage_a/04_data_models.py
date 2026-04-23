"""
Data Models for Stage A Research
Pydantic models for input/output validation
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StageAInput(BaseModel):
    """Input configuration for Stage A market research"""
    user_prompt: str = Field(
        ...,
        description="User's main research prompt/requirement (required)"
    )
    nganh_hang: str = Field(default="", description="Industry domain")
    thi_truong_muc_tieu: str = Field(default="", description="Target market")
    phan_khuc_quan_tam: List[str] = Field(default_factory=list, description="Segments of interest")
    doi_thu_seed: List[str] = Field(default_factory=list, description="Competitor seeds")
    khung_thoi_gian: str = Field(default="12 thang gan nhat", description="Time frame")
    muc_tieu_nghien_cuu: List[str] = Field(default_factory=list, description="Research objectives")


class EvidenceItem(BaseModel):
    """Individual evidence/source item"""
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None
    source_score: float = 0.0


class StageAOutput(BaseModel):
    """Output report for Stage A research"""
    tong_quan_thi_truong: str
    phan_tich_doi_thu: str
    xu_huong_nganh: str
    phan_khuc_va_insight_khach_hang: str
    citations: List[EvidenceItem]


class ClarificationResult(BaseModel):
    """Result of clarification process"""
    step: str  # "validation" | "waiting_for_input" | "completed"
    validation: dict
    request: dict
    clarified_input: StageAInput
    questions: List[str]
    suggestions: dict
    explanations: dict
    ready_to_proceed: bool
    has_gaps: bool
