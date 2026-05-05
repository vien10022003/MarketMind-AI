"""
Flask API Module
REST API endpoints for Stage A, B, C pipelines with streaming
"""

import json
import gc
import torch
from datetime import datetime
from flask import Flask, request, Response, stream_with_context
from rich import print as rprint

from .data_models import StageAInput, StageAOutput, EvidenceItem
from .environment import load_environment
from .llm_config import initialize_llm
from .clarification import clarify_user_prompt
from .router import classify_intent_and_respond
from .knowledge_handler import handle_knowledge_query
from .planning import planner_chain
from .react import run_react_loop
from .evidence_processing import normalize_and_filter_evidence
from .synthesis import synthesize_stage_a_report
from .output_formatting import build_markdown_report, convert_evidence_to_dict
from .mongodb import MongoDBManager

# Stage B & C imports
from stage_b.data_models_b import StageBInput, StageBOutput
from stage_b.campaign import run_stage_b_pipeline
from stage_c.data_models_c import StageCInput, CampaignLog
from stage_c.discord_publisher import run_stage_c_pipeline
from stage_c.campaign_log import save_campaign_log


# Initialize Flask app
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize components
try:
    # Clear GPU memory before initializing LLM
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        rprint("[yellow]🧹 GPU memory cleared[/yellow]")
    
    config = load_environment()
    llm = initialize_llm()
    mongo = MongoDBManager(config.get("mongo_uri"))
    rprint("[green]✅ All components initialized successfully[/green]")
except Exception as e:
    rprint(f"[red]Initialization error: {e}[/red]")
    llm = None
    mongo = None


@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    response.headers['Access-Control-Max-Age'] = '3600'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


def run_stage_a_pipeline_generator(req_data: dict):
    """Generator function for streaming pipeline execution"""
    rprint(f"[yellow][PIPELINE START] Input: {list(req_data.keys())}[/yellow]")

    try:
        # Validate input
        user_prompt = req_data.get("user_prompt", "").strip()
        if not user_prompt:
            yield json.dumps({
                "status": "error",
                "message": "Thiếu trường bắt buộc: user_prompt"
            }) + "\n"
            return

        yield json.dumps({
            "status": "progress",
            "message": f"Nhận được yêu cầu: {user_prompt[:100]}..."
        }) + "\n"

        # Create initial input
        initial_input = StageAInput(
            user_prompt=user_prompt,
            nganh_hang=req_data.get("nganh_hang", ""),
            thi_truong_muc_tieu=req_data.get("thi_truong_muc_tieu", ""),
            phan_khuc_quan_tam=req_data.get("phan_khuc_quan_tam", []),
            doi_thu_seed=req_data.get("doi_thu_seed", []),
            khung_thoi_gian=req_data.get("khung_thoi_gian", "12 thang gan nhat"),
            muc_tieu_nghien_cuu=req_data.get("muc_tieu_nghien_cuu", [])
        )

        # Check if nganh_hang is provided - if yes, skip intent routing and go directly to Stage A
        if initial_input.nganh_hang and initial_input.nganh_hang.strip():
            rprint("[magenta]nganh_hang provided, skipping intent routing and going directly to Stage A[/magenta]")
            yield json.dumps({
                "status": "progress",
                "message": "Đã nhận dạng ngành hàng, bắt đầu phân tích..."
            }) + "\n"
        else:
            # Step 0: Intent Routing
            rprint("[yellow][STEP 0] Intent Routing...[/yellow]")
            yield json.dumps({
                "status": "progress",
                "message": "Đang phân tích ý định..."
            }) + "\n"

            conversation_history = req_data.get("conversation_history", [])
            intent_result = classify_intent_and_respond(llm, user_prompt, conversation_history)
            detected_intent = intent_result.get("intent", "research")

            # ─── Path 1: Chat ───
            if detected_intent == "chat":
                rprint("[green]Chat intent detected, returning chat response[/green]")
                yield json.dumps({
                    "status": "chat_response",
                    "message": intent_result.get("response", "Xin chào! Bạn cần tôi giúp gì?"),
                }) + "\n"
                return

            # ─── Path 2: Knowledge (hard questions, may need Tavily search) ───
            if detected_intent == "knowledge":
                rprint("[cyan]Knowledge intent detected, processing...[/cyan]")
                for event in handle_knowledge_query(llm, user_prompt, conversation_history):
                    yield json.dumps(event) + "\n"
                return

            # ─── Path 3: Research / Marketing ───
            # If this is a fresh research request (not from form submission),
            # show the marketing form for the user to fill in details
            if not req_data.get("_from_marketing_form"):
                rprint("[magenta]Research intent detected, showing marketing form[/magenta]")
                yield json.dumps({
                    "status": "show_marketing_form",
                    "message": "Tôi nhận thấy bạn cần nghiên cứu thị trường. Vui lòng cung cấp thêm thông tin để tôi phân tích chính xác hơn.",
                    "detected_prompt": user_prompt,
                }) + "\n"
                return

        yield json.dumps({"status": "starting", "message": "Khởi tạo tác vụ Giai đoạn A..."}) + "\n"

        # Step 1: Use form data directly (skip LLM clarification since user already provided info)
        rprint("[yellow][STEP 1] Using marketing form data...[/yellow]")
        yield json.dumps({
            "status": "progress",
            "message": "Đang xử lý thông tin marketing..."
        }) + "\n"

        user_input = initial_input

        # Step 2: Planning
        rprint("[yellow][STEP 2] Planning...[/yellow]")
        yield json.dumps({
            "status": "progress",
            "message": "Đang lập kế hoạch (Planning)..."
        }) + "\n"

        plan = planner_chain(llm, user_input)

        yield json.dumps({
            "status": "plan_completed",
            "message": f"Lập kế hoạch hoàn tất: {len(plan.get('steps', []))} bước",
            "plan": plan
        }) + "\n"

        # Clear GPU memory after planning
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Step 3: ReAct Loop
        rprint("[yellow][STEP 3] ReAct Loop...[/yellow]")
        yield json.dumps({
            "status": "progress",
            "message": "Đang chạy tác vụ tìm kiếm..."
        }) + "\n"

        react_state = run_react_loop(llm, plan)

        yield json.dumps({
            "status": "react_completed",
            "message": f"Hoàn thành thu thập: {react_state['tool_calls']} phiên tìm kiếm",
            "react_summary": {
                "tool_calls": react_state.get("tool_calls", 0),
                "total_evidence": len(react_state.get("evidence", [])),
            }
        }) + "\n"

        # Clear GPU memory after ReAct
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Step 4: Evidence Processing
        rprint("[yellow][STEP 4] Evidence Processing...[/yellow]")
        yield json.dumps({
            "status": "progress",
            "message": "Lọc và chuẩn hóa dữ liệu..."
        }) + "\n"

        evidence_df = normalize_and_filter_evidence(react_state["evidence"])

        yield json.dumps({
            "status": "evidence_ready",
            "message": f"Còn lại {len(evidence_df)} chứng cứ hợp lệ",
            "evidence_count": {
                "raw": len(react_state.get("evidence", [])),
                "filtered": len(evidence_df)
            }
        }) + "\n"

        # Step 5: Synthesis
        rprint("[yellow][STEP 5] Synthesis...[/yellow]")
        yield json.dumps({
            "status": "progress",
            "message": "Đang tổng hợp báo cáo..."
        }) + "\n"

        try:
            stage_a_output = synthesize_stage_a_report(llm, user_input, evidence_df)
        except RuntimeError as e:
            # Handle out-of-memory errors
            if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
                rprint("[yellow]⚠️ Out of memory, reducing evidence and retrying...[/yellow]")
                yield json.dumps({
                    "status": "progress",
                    "message": "Giảm dung lượng dữ liệu, thử lại..."
                }) + "\n"
                
                # Reduce evidence to top 5 most relevant
                evidence_df = evidence_df.head(5)
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                try:
                    stage_a_output = synthesize_stage_a_report(llm, user_input, evidence_df)
                except Exception as retry_error:
                    rprint(f"[red]Synthesis retry failed: {str(retry_error)}[/red]")
                    yield json.dumps({
                        "status": "warning",
                        "message": "Báo cáo không thể tạo đầy đủ. Vui lòng thử lại với tiêu chí tìm kiếm cụ thể hơn.",
                    }) + "\n"
                    
                    # Return minimal output
                    stage_a_output = StageAOutput(
                        tong_quan_thi_truong="Quá nhiều dữ liệu để xử lý. Vui lòng thử lại với từ khóa tìm kiếm cụ thể hơn.",
                        phan_tich_doi_thu="",
                        xu_huong_nganh="",
                        phan_khuc_va_insight_khach_hang="",
                        citations=[]
                    )
            else:
                raise

        yield json.dumps({
            "status": "report_ready",
            "message": "Báo cáo đã tạo xong",
            "report": stage_a_output.model_dump(),
        }) + "\n"

        # Clear GPU memory after synthesis
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # Step 6: Save to MongoDB
        if mongo:
            rprint("[yellow][STEP 6] Saving to MongoDB...[/yellow]")
            yield json.dumps({
                "status": "progress",
                "message": "Đang lưu dữ liệu..."
            }) + "\n"

            metadata = {
                "timestamp": datetime.now().isoformat(),
                "input": user_input.model_dump(),
                "plan": plan,
                "react_summary": {
                    "tool_calls": react_state.get("tool_calls", 0),
                },
            }

            mongodb_id = mongo.save_report(metadata, stage_a_output)
        else:
            mongodb_id = None

        # Completion
        yield json.dumps({
            "status": "completed",
            "message": "Chiến dịch hoàn thành",
            "mongodb_id": mongodb_id,
            "timestamp": datetime.now().isoformat()
        }) + "\n"

    except Exception as e:
        rprint(f"[red][ERROR] {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        yield json.dumps({
            "status": "error",
            "message": f"Bị lỗi: {str(e)}"
        }) + "\n"


@app.route('/api/research/stage_a', methods=['POST', 'OPTIONS'])
def api_research_stage_a():
    """Main research endpoint - handles chat, knowledge, and initial research classification"""
    if request.method == 'OPTIONS':
        return '', 200

    rprint(f"[yellow][API] POST /api/research/stage_a[/yellow]")
    
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400

    return Response(
        stream_with_context(run_stage_a_pipeline_generator(data)),
        content_type='application/x-ndjson',
        status=200
    )


@app.route('/api/research/stage_a/marketing', methods=['POST', 'OPTIONS'])
def api_research_stage_a_marketing():
    """Marketing form submission endpoint - runs full Stage A pipeline skipping intent classification"""
    if request.method == 'OPTIONS':
        return '', 200

    rprint(f"[yellow][API] POST /api/research/stage_a/marketing[/yellow]")
    
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400

    # Mark this as coming from the marketing form so the pipeline skips
    # intent classification and goes straight to research
    data["_from_marketing_form"] = True

    return Response(
        stream_with_context(run_stage_a_pipeline_generator(data)),
        content_type='application/x-ndjson',
        status=200
    )


# ─── Stage B: Strategy Generation ────────────────────────────────────

def run_stage_b_generator(req_data: dict):
    """Generator for Stage B strategy pipeline streaming."""
    try:
        stage_b_input = StageBInput(
            stage_a_report=req_data.get("stage_a_report", {}),
            stage_a_input=req_data.get("stage_a_input", {}),
            mongodb_id=req_data.get("mongodb_id"),
        )

        if not stage_b_input.stage_a_report:
            yield json.dumps({"status": "error", "message": "Thiếu stage_a_report"}) + "\n"
            return

        for event in run_stage_b_pipeline(llm, stage_b_input):
            yield json.dumps(event) + "\n"

    except Exception as e:
        rprint(f"[red][STAGE B ERROR] {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        yield json.dumps({"status": "error", "message": f"Stage B lỗi: {str(e)}"}) + "\n"


@app.route('/api/strategy/stage_b', methods=['POST', 'OPTIONS'])
def api_strategy_stage_b():
    """Stage B: Generate marketing strategy from Stage A report."""
    if request.method == 'OPTIONS':
        return '', 200
    rprint(f"[yellow][API] POST /api/strategy/stage_b[/yellow]")
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400
    return Response(
        stream_with_context(run_stage_b_generator(data)),
        content_type='application/x-ndjson', status=200
    )


@app.route('/api/strategy/stage_b/approve', methods=['POST', 'OPTIONS'])
def api_strategy_stage_b_approve():
    """Stage B: Save approved/edited briefs."""
    if request.method == 'OPTIONS':
        return '', 200
    rprint(f"[yellow][API] POST /api/strategy/stage_b/approve[/yellow]")
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400

    # Save approved strategy + briefs to MongoDB
    if mongo and mongo.client:
        try:
            collection = mongo.db['stage_b_strategies']
            doc = {
                "timestamp": datetime.now().isoformat(),
                "mongodb_stage_a_id": data.get("mongodb_id"),
                "strategy": data.get("strategy", {}),
                "approved_briefs": data.get("approved_briefs", []),
            }
            result = collection.insert_one(doc)
            return {
                "status": "approved",
                "message": "Chiến lược đã được phê duyệt",
                "strategy_id": str(result.inserted_id),
            }, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    else:
        return {
            "status": "approved",
            "message": "Chiến lược đã được phê duyệt (MongoDB không khả dụng)",
        }, 200


# ─── Stage C: Campaign Execution ─────────────────────────────────────

def run_stage_c_generator(req_data: dict):
    """Generator for Stage C campaign execution streaming."""
    try:
        stage_c_input = StageCInput(
            approved_briefs=req_data.get("approved_briefs", []),
            webhook_url=req_data.get("webhook_url"),
            image_api_url=req_data.get("image_api_url"),
            skip_image_generation=req_data.get("skip_image_generation", False),
            mongodb_stage_a_id=req_data.get("mongodb_stage_a_id"),
        )

        for event in run_stage_c_pipeline(stage_c_input):
            yield json.dumps(event) + "\n"

            # Save campaign log to MongoDB when completed
            if event.get("status") == "stage_c_completed" and mongo:
                campaign_log_data = event.get("campaign_log", {})
                if campaign_log_data:
                    log = CampaignLog(**campaign_log_data)
                    log_id = save_campaign_log(mongo, log)
                    if log_id:
                        yield json.dumps({
                            "status": "progress",
                            "message": f"📝 Nhật ký chiến dịch đã lưu: {log_id}",
                        }) + "\n"

    except Exception as e:
        rprint(f"[red][STAGE C ERROR] {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        yield json.dumps({"status": "error", "message": f"Stage C lỗi: {str(e)}"}) + "\n"


@app.route('/api/campaign/stage_c', methods=['POST', 'OPTIONS'])
def api_campaign_stage_c():
    """Stage C: Execute approved campaign (image gen + Discord posting)."""
    if request.method == 'OPTIONS':
        return '', 200
    rprint(f"[yellow][API] POST /api/campaign/stage_c[/yellow]")
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400
    return Response(
        stream_with_context(run_stage_c_generator(data)),
        content_type='application/x-ndjson', status=200
    )


@app.route('/api/campaign/stage_c/scheduled', methods=['POST', 'OPTIONS'])
def api_campaign_stage_c_scheduled():
    """Stage C Scheduled: Schedule approved campaign with specific posting times."""
    if request.method == 'OPTIONS':
        return '', 200
    rprint(f"[yellow][API] POST /api/campaign/stage_c/scheduled[/yellow]")
    data = request.get_json()
    if not data:
        return {"error": "Missing JSON body"}, 400
    
    try:
        # Import scheduler
        from stage_c.campaign_scheduler import get_scheduler
        
        stage_c_input = StageCInput(
            approved_briefs=data.get("approved_briefs", []),
            webhook_url=data.get("webhook_url"),
            image_api_url=data.get("image_api_url"),
            skip_image_generation=data.get("skip_image_generation", False),
            mongodb_stage_a_id=data.get("mongodb_stage_a_id"),
            execution_mode="scheduled",  # Mark as scheduled mode
            scheduled_times=data.get("scheduled_times", []),  # List of ISO 8601 datetimes
        )
        
        def run_scheduled_stage_c_generator():
            """Generator for scheduled Stage C campaign."""
            for event in run_stage_c_pipeline(stage_c_input):
                yield json.dumps(event) + "\n"
        
        return Response(
            stream_with_context(run_scheduled_stage_c_generator()),
            content_type='application/x-ndjson', status=200
        )
    except Exception as e:
        rprint(f"[red][SCHEDULED STAGE C ERROR] {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500


# ─── Health Check ─────────────────────────────────────────────────────

# ─── Conversation History ─────────────────────────────────────────────────────

@app.route('/api/conversations', methods=['GET', 'OPTIONS'])
def api_list_conversations():
    """List recent conversations"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from conversation_manager import get_conversation_manager
        
        if not mongo or not mongo.db:
            return {"error": "MongoDB not available"}, 500
        
        cm = get_conversation_manager(mongo.db)
        skip = request.args.get('skip', default=0, type=int)
        limit = request.args.get('limit', default=10, type=int)
        
        conversations, total = cm.list_conversations(skip=skip, limit=limit)
        
        return {
            "data": {
                "conversations": conversations,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        }, 200
    except Exception as e:
        rprint(f"[red][LIST CONVERSATIONS ERROR] {str(e)}[/red]")
        return {"error": str(e)}, 500


@app.route('/api/conversations/<conversation_id>', methods=['GET', 'OPTIONS'])
def api_get_conversation(conversation_id):
    """Get a specific conversation"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from conversation_manager import get_conversation_manager
        
        if not mongo or not mongo.db:
            return {"error": "MongoDB not available"}, 500
        
        cm = get_conversation_manager(mongo.db)
        conversation = cm.get_conversation(conversation_id)
        
        if not conversation:
            return {"error": "Conversation not found"}, 404
        
        return {"data": conversation}, 200
    except Exception as e:
        rprint(f"[red][GET CONVERSATION ERROR] {str(e)}[/red]")
        return {"error": str(e)}, 500


@app.route('/api/conversations', methods=['POST', 'OPTIONS'])
def api_create_conversation():
    """Create a new conversation"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from conversation_manager import get_conversation_manager
        import uuid
        
        if not mongo or not mongo.db:
            return {"error": "MongoDB not available"}, 500
        
        data = request.get_json() or {}
        conversation_id = str(uuid.uuid4())
        title = data.get('title')
        
        cm = get_conversation_manager(mongo.db)
        conversation = cm.create_conversation(conversation_id, title=title)
        
        return {"data": conversation}, 201
    except Exception as e:
        rprint(f"[red][CREATE CONVERSATION ERROR] {str(e)}[/red]")
        return {"error": str(e)}, 500


@app.route('/api/conversations/<conversation_id>/messages', methods=['POST', 'OPTIONS'])
def api_save_messages(conversation_id):
    """Save one or more messages to conversation"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from conversation_manager import get_conversation_manager, ChatMessageDoc
        
        if not mongo or not mongo.db:
            return {"error": "MongoDB not available"}, 500
        
        data = request.get_json() or {}
        messages_data = data.get('messages', [])
        
        if not messages_data:
            return {"error": "No messages provided"}, 400
        
        # Convert to ChatMessageDoc
        messages = []
        for msg_data in messages_data:
            msg = ChatMessageDoc(
                id=msg_data.get('id'),
                type=msg_data.get('type'),
                content=msg_data.get('content', ''),
                timestamp=msg_data.get('timestamp', datetime.now().isoformat()),
                mongodbId=msg_data.get('mongodbId'),
                clarificationData=msg_data.get('clarificationData'),
                planData=msg_data.get('planData'),
                reactSummaryData=msg_data.get('reactSummaryData'),
                evidenceData=msg_data.get('evidenceData'),
                reportData=msg_data.get('reportData'),
                strategyData=msg_data.get('strategyData'),
                contentBriefsData=msg_data.get('contentBriefsData'),
                stageBProposalData=msg_data.get('stageBProposalData'),
                stageCProposalData=msg_data.get('stageCProposalData'),
                stageCScheduleProposalData=msg_data.get('stageCScheduleProposalData'),
                campaignLogData=msg_data.get('campaignLogData'),
                scheduleManagerData=msg_data.get('scheduleManagerData'),
                knowledgeData=msg_data.get('knowledgeData'),
                marketingFormData=msg_data.get('marketingFormData'),
            )
            messages.append(msg)
        
        cm = get_conversation_manager(mongo.db)
        success = cm.save_batch_messages(conversation_id, messages)
        
        if not success:
            return {"error": "Conversation not found or no changes made"}, 404
        
        return {"data": {"message_count": len(messages), "success": True}}, 200
    except Exception as e:
        rprint(f"[red][SAVE MESSAGES ERROR] {str(e)}[/red]")
        return {"error": str(e)}, 500


@app.route('/api/conversations/<conversation_id>/title', methods=['PUT', 'OPTIONS'])
def api_update_conversation_title(conversation_id):
    """Update conversation title"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from conversation_manager import get_conversation_manager
        
        if not mongo or not mongo.db:
            return {"error": "MongoDB not available"}, 500
        
        data = request.get_json() or {}
        title = data.get('title')
        
        if not title:
            return {"error": "Title is required"}, 400
        
        cm = get_conversation_manager(mongo.db)
        success = cm.update_title(conversation_id, title)
        
        if not success:
            return {"error": "Conversation not found"}, 404
        
        return {"data": {"success": True}}, 200
    except Exception as e:
        rprint(f"[red][UPDATE TITLE ERROR] {str(e)}[/red]")
        return {"error": str(e)}, 500


@app.route('/api/conversations/<conversation_id>', methods=['DELETE', 'OPTIONS'])
def api_delete_conversation(conversation_id):
    """Delete a conversation"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        from conversation_manager import get_conversation_manager
        
        if not mongo or not mongo.db:
            return {"error": "MongoDB not available"}, 500
        
        cm = get_conversation_manager(mongo.db)
        success = cm.delete_conversation(conversation_id)
        
        if not success:
            return {"error": "Conversation not found"}, 404
        
        return {"data": {"success": True}}, 200
    except Exception as e:
        rprint(f"[red][DELETE CONVERSATION ERROR] {str(e)}[/red]")
        return {"error": str(e)}, 500


# ─── Health Check ─────────────────────────────────────────────────────

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_ready": llm is not None,
        "mongodb_ready": mongo is not None and mongo.client is not None
    }, 200


def create_app():
    """Factory function to create Flask app"""
    return app
