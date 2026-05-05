"""
Flask App Initialization Example - Stage C Scheduler Integration

This example shows how to integrate the scheduled posting feature
into your existing Flask application.
"""

# In your flask_api.py or app.py, add this code at startup:

from flask import Flask
from stage_c import (
    initialize_scheduler,
    initialize_scheduler_service,
    create_scheduler_blueprint,
)


def initialize_stage_c_scheduler(app: Flask):
    """
    Initialize Stage C scheduler components.
    Call this after creating your Flask app but before running.
    
    Example:
        app = Flask(__name__)
        initialize_stage_c_scheduler(app)
        app.run()
    """
    
    # Step 1: Initialize MongoDB-backed campaign scheduler
    # This creates the scheduler instance and MongoDB collections
    print("📅 Initializing campaign scheduler...")
    initialize_scheduler()
    
    # Step 2: Start the background scheduler service
    # This runs a daemon thread that checks for pending briefs every 60 seconds
    print("🚀 Starting background scheduler service...")
    scheduler_service = initialize_scheduler_service(
        check_interval=60,  # Check every 60 seconds (adjust as needed)
        auto_start=True     # Automatically start the service
    )
    
    # Step 3: Register scheduler API routes
    # Adds endpoints like /api/stage-c/scheduler/status, /campaigns, etc.
    print("📡 Registering scheduler API routes...")
    scheduler_bp = create_scheduler_blueprint()
    app.register_blueprint(scheduler_bp)
    
    print("✅ Stage C scheduler initialized successfully!")
    print("📖 Available endpoints:")
    print("   - GET  /api/stage-c/scheduler/status")
    print("   - GET  /api/stage-c/scheduler/campaigns")
    print("   - GET  /api/stage-c/scheduler/campaigns/{campaign_id}")
    print("   - GET  /api/stage-c/scheduler/campaigns/{campaign_id}/results")
    print("   - GET  /api/stage-c/scheduler/pending")
    print("   - POST /api/stage-c/scheduler/start")
    print("   - POST /api/stage-c/scheduler/stop")
    print("   - POST /api/stage-c/scheduler/config")
    
    return scheduler_service


# ============================================================================
# COMPLETE FLASK APP EXAMPLE
# ============================================================================

if __name__ == "__main__":
    from flask import jsonify
    
    # Create Flask app
    app = Flask(__name__)
    
    # Initialize Stage C scheduler
    scheduler = initialize_stage_c_scheduler(app)
    
    # Your existing routes...
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"}), 200
    
    # Start Flask app
    print("\n🎯 MarketMind AI - Stage C with Scheduling")
    print("=" * 50)
    app.run(debug=True, port=5000)


# ============================================================================
# USING SCHEDULED POSTING IN YOUR CODE
# ============================================================================

"""
# When Stage C is called with scheduled mode:

from stage_c.data_models_c import StageCInput
from stage_c.discord_publisher import run_stage_c_pipeline

# Request from frontend with scheduled times
stage_c_input = StageCInput(
    approved_briefs=[
        {
            "id": "brief-1",
            "title": "Morning Announcement",
            "caption": "Check out our new product!",
            "image_prompt": "modern product showcase",
            "pillar": "Product",
            "content_type": "Announcement"
        },
        {
            "id": "brief-2",
            "title": "Community Update",
            "caption": "Updates from our team",
            "image_prompt": "team collaboration",
            "pillar": "Community",
            "content_type": "Update"
        }
    ],
    execution_mode="scheduled",  # <-- Use scheduled mode
    scheduled_times=[
        "2024-01-15T09:00:00Z",  # First brief posts at 9 AM UTC
        "2024-01-15T14:00:00Z"   # Second brief posts at 2 PM UTC
    ],
    mongodb_stage_a_id="stage_a_report_id",
)

# Stream the pipeline
for event in run_stage_c_pipeline(stage_c_input):
    if event["status"] == "stage_c_completed":
        print(f"Campaign {event['campaign_log']['campaign_id']} scheduled!")
        # Backend will now wait for the scheduler to post at scheduled times
    else:
        print(f"[{event['status']}] {event['message']}")
"""


# ============================================================================
# MONITORING SCHEDULED CAMPAIGNS
# ============================================================================

"""
# Example client code to monitor scheduled campaigns:

import requests
import json

API_BASE = "http://localhost:5000/api/stage-c/scheduler"

# 1. Check scheduler status
response = requests.get(f"{API_BASE}/status")
print(json.dumps(response.json(), indent=2))
# Output:
# {
#   "success": true,
#   "data": {
#     "running": true,
#     "pending_briefs": 5,
#     "check_interval": 60
#   }
# }

# 2. Get all campaigns
response = requests.get(f"{API_BASE}/campaigns")
print(json.dumps(response.json(), indent=2))

# 3. Get campaigns that are still scheduled
response = requests.get(f"{API_BASE}/campaigns?status=scheduled")
print(json.dumps(response.json(), indent=2))

# 4. Get pending briefs (ready to post now)
response = requests.get(f"{API_BASE}/pending")
print(json.dumps(response.json(), indent=2))
# Output:
# {
#   "success": true,
#   "data": {
#     "total_campaigns_pending": 1,
#     "total_briefs_pending": 2,
#     "campaigns": [...]
#   }
# }

# 5. Get specific campaign details
campaign_id = "abc12345"
response = requests.get(f"{API_BASE}/campaigns/{campaign_id}")
print(json.dumps(response.json(), indent=2))

# 6. Get campaign execution results
response = requests.get(f"{API_BASE}/campaigns/{campaign_id}/results")
results = response.json()["data"]
for result in results["results"]:
    print(f"
{result['brief_title']}: {result['status']} ({result['posted_at']})")

# 7. Control scheduler
# Start
requests.post(f"{API_BASE}/scheduler/start")

# Stop
requests.post(f"{API_BASE}/scheduler/stop")

# Configure check interval (seconds)
requests.post(
    f"{API_BASE}/scheduler/config",
    json={"check_interval": 30}
)
"""
