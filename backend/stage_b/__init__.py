"""
Stage B Strategy Building Package
Transforms Stage A research report into marketing strategy and content briefs for Discord.
Pipeline: SWOT → USP → Persona → Content Pillars → Campaign Plan → Content Briefs
"""

from .data_models_b import (
    SWOTAnalysis,
    USPResult,
    BuyerPersona,
    ContentPillar,
    ScheduleEntry,
    CampaignPlan,
    ContentBrief,
    StageBInput,
    StageBOutput,
)
from .strategy import (
    generate_swot_analysis,
    extract_usp,
    refine_persona,
    define_content_pillars,
)
from .campaign import (
    create_campaign_plan,
    generate_content_briefs,
    run_stage_b_pipeline,
)

__version__ = "1.0.0"
__all__ = [
    "SWOTAnalysis",
    "USPResult",
    "BuyerPersona",
    "ContentPillar",
    "ScheduleEntry",
    "CampaignPlan",
    "ContentBrief",
    "StageBInput",
    "StageBOutput",
    "generate_swot_analysis",
    "extract_usp",
    "refine_persona",
    "define_content_pillars",
    "create_campaign_plan",
    "generate_content_briefs",
    "run_stage_b_pipeline",
]
