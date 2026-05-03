"""
Campaign Log Module - Stage C
MongoDB logging for campaign execution results.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from rich import print as rprint

from .data_models_c import CampaignLog


def save_campaign_log(mongo, campaign_log: CampaignLog) -> Optional[str]:
    """
    Save campaign execution log to MongoDB.
    
    Args:
        mongo: MongoDBManager instance
        campaign_log: CampaignLog to save
    
    Returns:
        MongoDB document ID or None
    """
    if not mongo or not mongo.client:
        rprint("[yellow]⚠️ MongoDB not connected. Skipping campaign log save.[/yellow]")
        return None

    try:
        collection = mongo.db['campaign_logs']
        doc = {
            "campaign_id": campaign_log.campaign_id,
            "mongodb_stage_a_id": campaign_log.mongodb_stage_a_id,
            "results": [r.model_dump() for r in campaign_log.results],
            "total_briefs": campaign_log.total_briefs,
            "total_posted": campaign_log.total_posted,
            "total_failed": campaign_log.total_failed,
            "total_skipped": campaign_log.total_skipped,
            "started_at": campaign_log.started_at,
            "completed_at": campaign_log.completed_at or datetime.now().isoformat(),
        }

        result = collection.insert_one(doc)
        doc_id = str(result.inserted_id)
        rprint(f"[green]✅ Campaign log saved: {doc_id}[/green]")
        return doc_id

    except Exception as e:
        rprint(f"[red]❌ Failed to save campaign log: {e}[/red]")
        return None


def get_campaign_log(mongo, campaign_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve campaign log by campaign_id."""
    if not mongo or not mongo.client:
        return None

    try:
        collection = mongo.db['campaign_logs']
        return collection.find_one({"campaign_id": campaign_id})
    except Exception as e:
        rprint(f"[red]❌ Failed to retrieve campaign log: {e}[/red]")
        return None
