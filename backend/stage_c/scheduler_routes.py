"""
Scheduler API Routes - Stage C
Provides endpoints to manage and monitor scheduled campaigns.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from typing import Optional
from rich import print as rprint

from .campaign_scheduler import get_scheduler
from .scheduler_service import get_scheduler_service


def create_scheduler_blueprint() -> Blueprint:
    """Create Flask blueprint for scheduler endpoints"""
    bp = Blueprint("scheduler", __name__, url_prefix="/api/stage-c/scheduler")
    
    @bp.route("/<path:path>", methods=["OPTIONS"])
    @bp.route("/", methods=["OPTIONS"])
    def handle_options(path=None):
        """Handle CORS preflight requests"""
        return '', 200
    
    @bp.route("/status", methods=["GET"])
    def get_scheduler_status():
        """Get current scheduler service status"""
        try:
            service = get_scheduler_service()
            status = service.get_status()
            return jsonify({
                "success": True,
                "data": status
            }), 200
        except Exception as e:
            rprint(f"[red]Error getting scheduler status: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/campaigns", methods=["GET"])
    def list_campaigns():
        """List all campaigns with optional status filter"""
        try:
            scheduler = get_scheduler()
            status = request.args.get("status")  # scheduled, completed, failed, etc.
            
            campaigns = scheduler.get_all_campaigns(status=status)
            
            return jsonify({
                "success": True,
                "data": {
                    "total": len(campaigns),
                    "campaigns": campaigns,
                    "filter": {"status": status} if status else None
                }
            }), 200
        except Exception as e:
            rprint(f"[red]Error listing campaigns: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/campaigns/<campaign_id>", methods=["GET"])
    def get_campaign(campaign_id: str):
        """Get detailed information about a specific campaign"""
        try:
            scheduler = get_scheduler()
            campaign = scheduler.get_campaign_history(campaign_id)
            
            if not campaign:
                return jsonify({
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }), 404
            
            return jsonify({
                "success": True,
                "data": campaign
            }), 200
        except Exception as e:
            rprint(f"[red]Error getting campaign {campaign_id}: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/campaigns/<campaign_id>/results", methods=["GET"])
    def get_campaign_results(campaign_id: str):
        """Get execution results of a campaign"""
        try:
            scheduler = get_scheduler()
            campaign = scheduler.get_campaign_history(campaign_id)
            
            if not campaign:
                return jsonify({
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }), 404
            
            results = campaign.get("execution_results", [])
            
            return jsonify({
                "success": True,
                "data": {
                    "campaign_id": campaign_id,
                    "status": campaign.get("status"),
                    "total_results": len(results),
                    "posted_count": campaign.get("posted_count", 0),
                    "failed_count": campaign.get("failed_count", 0),
                    "results": results
                }
            }), 200
        except Exception as e:
            rprint(f"[red]Error getting campaign results: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/pending", methods=["GET"])
    def get_pending_briefs():
        """Get all briefs pending for posting"""
        try:
            scheduler = get_scheduler()
            pending = scheduler.get_pending_briefs()
            
            # Format for response
            formatted_pending = []
            for campaign_info in pending:
                formatted_pending.append({
                    "campaign_id": campaign_info["campaign_id"],
                    "mongodb_id": campaign_info["mongodb_id"],
                    "pending_briefs_count": len(campaign_info["briefs_to_post"]),
                    "briefs_preview": [
                        {
                            "index": idx,
                            "title": brief.get("title", f"Brief {idx}"),
                            "scheduled_time": campaign_info["campaign_doc"]["scheduled_times"][idx]
                        }
                        for idx, brief in campaign_info["briefs_to_post"]
                    ]
                })
            
            return jsonify({
                "success": True,
                "data": {
                    "total_campaigns_pending": len(pending),
                    "total_briefs_pending": sum(len(x["briefs_to_post"]) for x in pending),
                    "campaigns": formatted_pending
                }
            }), 200
        except Exception as e:
            rprint(f"[red]Error getting pending briefs: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/scheduler/start", methods=["POST"])
    def start_scheduler():
        """Start the background scheduler service"""
        try:
            service = get_scheduler_service()
            
            if service.running:
                return jsonify({
                    "success": True,
                    "message": "Scheduler already running",
                    "status": service.get_status()
                }), 200
            
            service.start()
            
            return jsonify({
                "success": True,
                "message": "Scheduler started",
                "status": service.get_status()
            }), 200
        except Exception as e:
            rprint(f"[red]Error starting scheduler: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/scheduler/stop", methods=["POST"])
    def stop_scheduler():
        """Stop the background scheduler service"""
        try:
            service = get_scheduler_service()
            
            if not service.running:
                return jsonify({
                    "success": True,
                    "message": "Scheduler already stopped",
                    "status": service.get_status()
                }), 200
            
            service.stop()
            
            return jsonify({
                "success": True,
                "message": "Scheduler stopped",
                "status": service.get_status()
            }), 200
        except Exception as e:
            rprint(f"[red]Error stopping scheduler: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.route("/scheduler/config", methods=["POST"])
    def configure_scheduler():
        """Configure scheduler settings"""
        try:
            data = request.get_json() or {}
            check_interval = data.get("check_interval", 60)
            
            service = get_scheduler_service()
            service.check_interval = check_interval
            
            return jsonify({
                "success": True,
                "message": f"Scheduler configured with {check_interval}s check interval",
                "config": {
                    "check_interval": service.check_interval
                }
            }), 200
        except Exception as e:
            rprint(f"[red]Error configuring scheduler: {e}[/red]")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @bp.after_request
    def add_cors_headers(response):
        """Add CORS headers to all scheduler blueprint responses"""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.headers['Access-Control-Max-Age'] = '3600'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    return bp
