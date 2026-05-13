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
    ban_chat_san_pham: str = Field(default="", description="Bản chất sản phẩm (Tên, danh mục, mô tả, tính năng, USP)")
    khach_hang_muc_tieu: str = Field(default="", description="Khách hàng mục tiêu (Ai, nhu cầu, nỗi đau, thói quen)")
    gia_tri_cot_loi: str = Field(default="", description="Giá trị cốt lõi & Lý do mua hàng (Giải quyết vấn đề, lợi ích, bằng chứng xã hội)")
    gia_ca_chinh_sach: str = Field(default="", description="Giá cả & Chính sách (Giá bán, bảo hành, khuyến mãi)")


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
