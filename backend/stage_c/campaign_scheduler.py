"""
Campaign Scheduler Module - Stage C
Manages scheduled posting of content briefs to Discord.
Stores scheduled posts in MongoDB and handles delayed execution.
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from pymongo import MongoClient
from bson import ObjectId
from rich import print as rprint

from .data_models_c import ExecutionResult, CampaignLog


class CampaignScheduler:
    """Manages scheduled campaigns and posts"""
    
    def __init__(self, mongodb_uri: Optional[str] = None):
        """Initialize scheduler with MongoDB connection"""
        self.mongodb_uri = mongodb_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client.get_database("marketmind")
        self.scheduled_campaigns = self.db["scheduled_campaigns"]
        self.campaign_logs = self.db["campaign_logs"]
        
        # Ensure indexes
        self.scheduled_campaigns.create_index("scheduled_post_times")
        self.scheduled_campaigns.create_index("status")
        self.campaign_logs.create_index("campaign_id")
    
    def save_scheduled_campaign(
        self,
        campaign_id: str,
        mongodb_stage_a_id: str,
        briefs: List[Dict[str, Any]],
        scheduled_times: List[str],
        webhook_url: str,
        image_api_url: Optional[str] = None,
        skip_images: bool = False,
    ) -> str:
        """
        Save a scheduled campaign to MongoDB.
        
        Args:
            campaign_id: Unique campaign identifier
            mongodb_stage_a_id: Reference to Stage A report
            briefs: List of content briefs
            scheduled_times: List of ISO datetimes for posting
            webhook_url: Discord webhook URL
            image_api_url: Image API URL
            skip_images: Whether to skip image generation
        
        Returns:
            MongoDB document ID
        """
        doc = {
            "campaign_id": campaign_id,
            "mongodb_stage_a_id": mongodb_stage_a_id,
            "briefs": briefs,
            "scheduled_times": scheduled_times,
            "webhook_url": webhook_url,
            "image_api_url": image_api_url,
            "skip_images": skip_images,
            "status": "scheduled",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "execution_results": [],
            "posted_count": 0,
            "failed_count": 0,
            "total_scheduled": len(briefs),
        }
        
        result = self.scheduled_campaigns.insert_one(doc)
        rprint(f"[green]✅ Campaign {campaign_id} saved to scheduler[/green]")
        return str(result.inserted_id)
    
    def get_pending_briefs(self) -> List[Dict[str, Any]]:
        """
        Get all briefs that need to be posted now or soon.
        
        Returns:
            List of campaign docs with briefs ready to post
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Find campaigns with scheduled times <= now and status = scheduled
        pending = list(self.scheduled_campaigns.find({
            "status": "scheduled",
            "scheduled_times": {"$exists": True}
        }))
        
        result = []
        for campaign in pending:
            briefs_to_post = []
            for idx, brief in enumerate(campaign.get("briefs", [])):
                if idx < len(campaign.get("scheduled_times", [])):
                    scheduled_time = campaign["scheduled_times"][idx]
                    if scheduled_time <= now:
                        briefs_to_post.append((idx, brief))
            
            if briefs_to_post:
                result.append({
                    "campaign_id": campaign["campaign_id"],
                    "mongodb_id": str(campaign["_id"]),
                    "briefs_to_post": briefs_to_post,
                    "campaign_doc": campaign,
                })
        
        return result
    
    def update_brief_result(
        self,
        campaign_id: str,
        brief_index: int,
        result: ExecutionResult,
    ) -> None:
        """
        Update the result of a posted brief.
        
        Args:
            campaign_id: Campaign identifier
            brief_index: Index of the brief in the campaign
            result: ExecutionResult with posting details
        """
        self.scheduled_campaigns.update_one(
            {"campaign_id": campaign_id},
            {
                "$push": {"execution_results": result.model_dump()},
                "$inc": {
                    "posted_count": 1 if result.discord_sent else 0,
                    "failed_count": 1 if result.status == "failed" else 0,
                }
            }
        )
    
    def mark_campaign_complete(self, campaign_id: str) -> None:
        """Mark a campaign as fully executed"""
        self.scheduled_campaigns.update_one(
            {"campaign_id": campaign_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            }
        )
    
    def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a campaign"""
        return self.scheduled_campaigns.find_one({"campaign_id": campaign_id})
    
    def get_all_campaigns(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all campaigns, optionally filtered by status.
        
        Args:
            status: Filter by status (scheduled, completed, failed, etc.)
        
        Returns:
            List of campaign documents
        """
        query = {}
        if status:
            query["status"] = status
        
        campaigns = list(self.scheduled_campaigns.find(query).sort("created_at", -1))
        
        # Convert ObjectId to string for JSON serialization
        for campaign in campaigns:
            campaign["_id"] = str(campaign["_id"])
        
        return campaigns
    
    def get_pending_briefs_count(self) -> int:
        """Get count of briefs pending posting"""
        now = datetime.now(timezone.utc).isoformat()
        campaigns = self.scheduled_campaigns.find({"status": "scheduled"})
        
        count = 0
        for campaign in campaigns:
            for idx, scheduled_time in enumerate(campaign.get("scheduled_times", [])):
                if scheduled_time <= now:
                    count += 1
        
        return count
    
    def get_campaign_history(
        self,
        campaign_id: str,
        limit: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed history of a campaign including all results.
        
        Args:
            campaign_id: Campaign identifier
            limit: Max results to return
        
        Returns:
            Campaign document with full execution history
        """
        campaign = self.scheduled_campaigns.find_one({"campaign_id": campaign_id})
        if campaign:
            campaign["_id"] = str(campaign["_id"])
            # Limit results array
            if "execution_results" in campaign:
                campaign["execution_results"] = campaign["execution_results"][-limit:]
        return campaign
    
    def close(self) -> None:
        """Close MongoDB connection"""
        self.client.close()


# Global scheduler instance
_scheduler: Optional[CampaignScheduler] = None


def get_scheduler() -> CampaignScheduler:
    """Get or create the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = CampaignScheduler()
    return _scheduler


def initialize_scheduler(mongodb_uri: Optional[str] = None) -> CampaignScheduler:
    """Initialize the global scheduler instance"""
    global _scheduler
    _scheduler = CampaignScheduler(mongodb_uri)
    return _scheduler
