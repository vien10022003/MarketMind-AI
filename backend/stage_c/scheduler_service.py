"""
Background Campaign Scheduler Service - Stage C
Monitors and executes scheduled campaigns at their designated times.
Runs as a background service that checks for pending posts every interval.
"""

import asyncio
import time
import threading
from datetime import datetime, timezone
from typing import Optional, Callable
from rich import print as rprint

from .campaign_scheduler import CampaignScheduler, get_scheduler
from .discord_publisher import post_to_discord, format_discord_embed
from .image_generator import generate_image, check_image_api_health, get_image_api_url
from .data_models_c import ExecutionResult


class SchedulerService:
    """Background service for executing scheduled campaigns"""
    
    def __init__(
        self,
        scheduler: Optional[CampaignScheduler] = None,
        check_interval: int = 60,  # Check every 60 seconds
        on_post_callback: Optional[Callable] = None,
    ):
        """
        Initialize the scheduler service.
        
        Args:
            scheduler: CampaignScheduler instance (uses global if not provided)
            check_interval: How often to check for pending briefs (seconds)
            on_post_callback: Optional callback function for notifications
        """
        self.scheduler = scheduler or get_scheduler()
        self.check_interval = check_interval
        self.on_post_callback = on_post_callback
        self.running = False
        self._thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start the scheduler service in a background thread"""
        if self.running:
            rprint("[yellow]⚠️ Scheduler service already running[/yellow]")
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        rprint(f"[green]✅ Campaign scheduler started (check interval: {self.check_interval}s)[/green]")
    
    def stop(self) -> None:
        """Stop the scheduler service"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        rprint("[yellow]⏸️ Campaign scheduler stopped[/yellow]")
    
    def _run_loop(self) -> None:
        """Main loop that runs in background thread"""
        rprint("[blue]🔄 Scheduler service loop started[/blue]")
        
        while self.running:
            try:
                # Get all pending briefs
                pending_campaigns = self.scheduler.get_pending_briefs()
                
                if pending_campaigns:
                    rprint(f"[cyan]📋 Found {len(pending_campaigns)} campaigns with pending briefs[/cyan]")
                    
                    for campaign_info in pending_campaigns:
                        self._execute_campaign(campaign_info)
                
                # Sleep before next check
                time.sleep(self.check_interval)
            
            except Exception as e:
                rprint(f"[red]❌ Error in scheduler loop: {e}[/red]")
                time.sleep(self.check_interval)
    
    def _execute_campaign(self, campaign_info: dict) -> None:
        """
        Execute all pending briefs in a campaign.
        
        Args:
            campaign_info: Campaign info dict from get_pending_briefs
        """
        campaign_id = campaign_info["campaign_id"]
        mongodb_id = campaign_info["mongodb_id"]
        briefs_to_post = campaign_info["briefs_to_post"]
        campaign_doc = campaign_info["campaign_doc"]
        
        webhook_url = campaign_doc.get("webhook_url")
        image_api_url = get_image_api_url()
        skip_images = campaign_doc.get("skip_images", False)
        briefs = campaign_doc.get("briefs", [])
        scheduled_times = campaign_doc.get("scheduled_times", [])
        
        rprint(f"[cyan]📅 Executing campaign {campaign_id}: {len(briefs_to_post)} briefs[/cyan]")
        
        # Check image API availability once
        image_api_available = False
        if not skip_images and image_api_url:
            image_api_available = check_image_api_health(image_api_url)
        
        all_complete = True
        
        for brief_index, brief_data in briefs_to_post:
            brief_id = brief_data.get("id", f"brief-{brief_index + 1}")
            brief_title = brief_data.get("title", f"Bài đăng {brief_index + 1}")
            scheduled_time = scheduled_times[brief_index] if brief_index < len(scheduled_times) else None
            
            try:
                rprint(f"[cyan]📝 Processing: {brief_title}[/cyan]")
                
                # Generate image if needed
                image_url = None
                image_skipped = True
                
                if image_api_available and not skip_images:
                    image_prompt = brief_data.get("image_prompt", "")
                    if image_prompt:
                        try:
                            image_url = generate_image(image_prompt, image_api_url)
                            image_skipped = False
                            rprint(f"[green]✅ Image generated for {brief_title}[/green]")
                        except Exception as e:
                            rprint(f"[yellow]⚠️ Failed to generate image: {e}[/yellow]")
                
                # Format Discord embed
                payload = format_discord_embed(
                    title=brief_title,
                    caption=brief_data.get("caption", ""),
                    image_url=image_url,
                    color=brief_data.get("embed_color", 0x5865F2),
                    pillar=brief_data.get("pillar", ""),
                    content_type=brief_data.get("content_type", ""),
                    day=brief_data.get("scheduled_day", brief_index + 1),
                )
                
                # Post to Discord
                success = post_to_discord(payload, webhook_url)
                
                # Create execution result
                exec_result = ExecutionResult(
                    brief_id=brief_id,
                    brief_title=brief_title,
                    status="success" if success else "failed",
                    image_url=image_url,
                    image_skipped=image_skipped,
                    discord_sent=success,
                    error=None if success else "Discord post failed",
                    scheduled_post_time=scheduled_time,
                    posted_at=datetime.now(timezone.utc).isoformat(),
                )
                
                # Save result to scheduler
                self.scheduler.update_brief_result(campaign_id, brief_index, exec_result)
                
                if success:
                    rprint(f"[green]✅ Posted: {brief_title}[/green]")
                    if self.on_post_callback:
                        self.on_post_callback({
                            "campaign_id": campaign_id,
                            "brief_title": brief_title,
                            "status": "success",
                        })
                else:
                    rprint(f"[red]❌ Failed to post: {brief_title}[/red]")
                    all_complete = False
                    if self.on_post_callback:
                        self.on_post_callback({
                            "campaign_id": campaign_id,
                            "brief_title": brief_title,
                            "status": "failed",
                        })
            
            except Exception as e:
                rprint(f"[red]❌ Error processing {brief_title}: {e}[/red]")
                all_complete = False
                
                exec_result = ExecutionResult(
                    brief_id=brief_id,
                    brief_title=brief_title,
                    status="failed",
                    error=str(e),
                    scheduled_post_time=scheduled_time,
                )
                self.scheduler.update_brief_result(campaign_id, brief_index, exec_result)
        
        # Mark campaign complete if all briefs processed
        if all_complete:
            self.scheduler.mark_campaign_complete(campaign_id)
            rprint(f"[green]🎉 Campaign {campaign_id} completed![/green]")
    
    def get_status(self) -> dict:
        """Get current status of the scheduler service"""
        pending_count = self.scheduler.get_pending_briefs_count()
        return {
            "running": self.running,
            "pending_briefs": pending_count,
            "check_interval": self.check_interval,
        }


# Global scheduler service instance
_service: Optional[SchedulerService] = None


def get_scheduler_service(
    scheduler: Optional[CampaignScheduler] = None,
    check_interval: int = 60,
) -> SchedulerService:
    """Get or create the global scheduler service instance"""
    global _service
    if _service is None:
        _service = SchedulerService(scheduler, check_interval)
    return _service


def initialize_scheduler_service(
    scheduler: Optional[CampaignScheduler] = None,
    check_interval: int = 60,
    auto_start: bool = True,
) -> SchedulerService:
    """Initialize and optionally start the global scheduler service"""
    global _service
    _service = SchedulerService(scheduler, check_interval)
    
    if auto_start:
        _service.start()
    
    return _service
