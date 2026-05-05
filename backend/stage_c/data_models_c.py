"""
Data Models for Stage C Campaign Execution
Pydantic models for image generation, Discord publishing, and campaign logging
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ExecutionResult(BaseModel):
    """Result of executing a single content brief"""
    brief_id: str = Field(default="", description="ID of the content brief")
    brief_title: str = Field(default="", description="Title of the brief")
    status: str = Field(default="pending", description="pending | scheduled | success | failed | skipped")
    image_url: Optional[str] = Field(default=None, description="Generated image URL")
    image_skipped: bool = Field(default=False, description="Whether image gen was skipped")
    discord_sent: bool = Field(default=False, description="Whether Discord post succeeded")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    scheduled_post_time: Optional[str] = Field(default=None, description="ISO datetime for scheduled posting")
    posted_at: Optional[str] = Field(default=None, description="ISO datetime when actually posted")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class CampaignLog(BaseModel):
    """Log of entire campaign execution"""
    campaign_id: str = Field(default="", description="Campaign identifier")
    mongodb_stage_a_id: Optional[str] = Field(default=None, description="Original Stage A report ID")
    results: List[ExecutionResult] = Field(default_factory=list)
    total_briefs: int = Field(default=0)
    total_posted: int = Field(default=0)
    total_scheduled: int = Field(default=0)
    total_failed: int = Field(default=0)
    total_skipped: int = Field(default=0)
    execution_mode: str = Field(default="immediate", description="immediate | scheduled")
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = Field(default=None)


class StageCInput(BaseModel):
    """Input for Stage C pipeline"""
    approved_briefs: List[dict] = Field(default_factory=list, description="List of approved content briefs")
    webhook_url: Optional[str] = Field(default=None, description="Discord webhook URL override")
    skip_image_generation: bool = Field(default=False, description="Skip image generation")
    mongodb_stage_a_id: Optional[str] = Field(default=None, description="Stage A report MongoDB ID")
    execution_mode: str = Field(default="immediate", description="immediate | scheduled")
    scheduled_times: Optional[List[str]] = Field(default=None, description="List of ISO datetimes for scheduled posting (one per brief)")
