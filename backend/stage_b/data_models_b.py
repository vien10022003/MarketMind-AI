"""
Data Models for Stage B Strategy Building
Pydantic models for SWOT, USP, Persona, Content Pillars, Campaign Plan, and Content Briefs
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class SWOTAnalysis(BaseModel):
    """SWOT Analysis result"""
    strengths: List[str] = Field(default_factory=list, description="Điểm mạnh")
    weaknesses: List[str] = Field(default_factory=list, description="Điểm yếu")
    opportunities: List[str] = Field(default_factory=list, description="Cơ hội")
    threats: List[str] = Field(default_factory=list, description="Thách thức")


class USPResult(BaseModel):
    """Unique Selling Proposition result"""
    usp_statement: str = Field(default="", description="Tuyên bố USP chính")
    supporting_points: List[str] = Field(default_factory=list, description="Các điểm hỗ trợ USP")
    competitive_advantage: str = Field(default="", description="Lợi thế cạnh tranh nổi bật")


class BuyerPersona(BaseModel):
    """Buyer Persona refined for Discord marketing"""
    name: str = Field(default="", description="Tên persona (VD: 'Minh - Gen Z Explorer')")
    age_range: str = Field(default="", description="Độ tuổi (VD: '18-25')")
    interests: List[str] = Field(default_factory=list, description="Sở thích")
    pain_points: List[str] = Field(default_factory=list, description="Vấn đề/nỗi đau")
    discord_behavior: str = Field(default="", description="Hành vi trên Discord")
    preferred_content_types: List[str] = Field(
        default_factory=list,
        description="Loại nội dung ưa thích (VD: memes, infographic, tips)"
    )
    goals: List[str] = Field(default_factory=list, description="Mục tiêu của persona")


class ContentPillar(BaseModel):
    """Content Pillar - chủ đề nội dung chính"""
    name: str = Field(default="", description="Tên trụ cột nội dung")
    description: str = Field(default="", description="Mô tả chi tiết")
    example_topics: List[str] = Field(default_factory=list, description="Ví dụ chủ đề cụ thể")
    emoji: str = Field(default="📌", description="Emoji đại diện")


class ScheduleEntry(BaseModel):
    """Single schedule entry in campaign plan"""
    day: int = Field(default=1, description="Ngày thứ mấy trong campaign (1-based)")
    time: str = Field(default="19:00", description="Giờ đăng (HH:MM)")
    content_type: str = Field(default="", description="Loại nội dung")
    pillar_name: str = Field(default="", description="Thuộc content pillar nào")


class CampaignPlan(BaseModel):
    """Campaign Plan - lịch đăng tổng thể"""
    duration_days: int = Field(default=7, description="Số ngày chiến dịch")
    posting_frequency: str = Field(default="1 post/ngày", description="Tần suất đăng")
    content_types: List[str] = Field(default_factory=list, description="Các loại content sử dụng")
    schedule: List[ScheduleEntry] = Field(default_factory=list, description="Lịch đăng chi tiết")
    campaign_goal: str = Field(default="", description="Mục tiêu chiến dịch")


class ContentBrief(BaseModel):
    """Content Brief for a single Discord post"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8], description="ID brief")
    title: str = Field(default="", description="Tiêu đề bài đăng")
    caption: str = Field(default="", description="Nội dung caption/description")
    image_prompt: str = Field(default="", description="Prompt để sinh ảnh AI")
    content_type: str = Field(default="", description="Loại nội dung (tip, meme, infographic...)")
    pillar: str = Field(default="", description="Thuộc content pillar nào")
    scheduled_day: int = Field(default=1, description="Ngày đăng trong campaign")
    scheduled_time: str = Field(default="19:00", description="Giờ đăng")
    status: str = Field(default="pending", description="pending | approved | rejected | edited")
    embed_color: int = Field(default=0x5865F2, description="Màu embed Discord (hex)")


class StageBInput(BaseModel):
    """Input for Stage B pipeline"""
    stage_a_report: dict = Field(default_factory=dict, description="Stage A report data")
    stage_a_input: dict = Field(default_factory=dict, description="Stage A input config")
    mongodb_id: Optional[str] = Field(default=None, description="MongoDB ID of Stage A report")


class StageBOutput(BaseModel):
    """Complete output of Stage B pipeline"""
    swot: SWOTAnalysis = Field(default_factory=SWOTAnalysis)
    usp: USPResult = Field(default_factory=USPResult)
    persona: BuyerPersona = Field(default_factory=BuyerPersona)
    content_pillars: List[ContentPillar] = Field(default_factory=list)
    campaign_plan: CampaignPlan = Field(default_factory=CampaignPlan)
    content_briefs: List[ContentBrief] = Field(default_factory=list)
