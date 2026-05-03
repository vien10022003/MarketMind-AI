"""
Stage C Campaign Execution Package
Executes approved content briefs: Image generation → Discord posting → Logging.
"""

from .data_models_c import (
    ExecutionResult,
    CampaignLog,
    StageCInput,
)
from .image_generator import (
    generate_image,
    generate_batch_images,
    check_image_api_health,
)
from .discord_publisher import (
    format_discord_embed,
    post_to_discord,
    run_stage_c_pipeline,
)
from .campaign_log import (
    save_campaign_log,
    get_campaign_log,
)

__version__ = "1.0.0"
__all__ = [
    "ExecutionResult",
    "CampaignLog",
    "StageCInput",
    "generate_image",
    "generate_batch_images",
    "check_image_api_health",
    "format_discord_embed",
    "post_to_discord",
    "run_stage_c_pipeline",
    "save_campaign_log",
    "get_campaign_log",
]
