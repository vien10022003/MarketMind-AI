"""
Flask API Module
REST API endpoints for Stage A research pipeline with streaming
"""

import json
from datetime import datetime
from flask import Flask, request, Response, stream_with_context
from rich import print as rprint

from .04_data_models import StageAInput
from .02_environment import load_environment
from .03_llm_config import initialize_llm
from .05_clarification import clarify_user_prompt
from .06_planning import planner_chain
from .08_react import run_react_loop
from .09_evidence_processing import normalize_and_filter_evidence, convert_evidence_to_dict
from .10_synthesis import synthesize_stage_a_report
from .11_output_formatting import build_markdown_report
from .12_mongodb import MongoDBManager


# Initialize Flask app
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize components
try:
    config = load_environment()
    llm = initialize_llm()
    mongo = MongoDBManager(config.get("mongo_uri"))
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
    yield json.dumps({"status": "starting", "message": "Khởi tạo tác vụ Giai đoạn A..."}) + "\n"

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

        # Step 1: Clarification
        rprint("[yellow][STEP 1] Clarification...[/yellow]")
        yield json.dumps({
            "status": "progress",
            "message": "LLM đang phân tích yêu cầu..."
        }) + "\n"

        clarification_result = clarify_user_prompt(llm, user_prompt, initial_input)
        user_input = clarification_result["clarified_input"]

        yield json.dumps({
            "status": "clarification_provided",
            "message": "LLM đã phân tích ✅",
            "detected_info": {
                "nganh_hang": user_input.nganh_hang,
                "thi_truong_muc_tieu": user_input.thi_truong_muc_tieu,
            },
            "questions": clarification_result.get("questions", []),
        }) + "\n"

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

        stage_a_output = synthesize_stage_a_report(llm, user_input, evidence_df)

        yield json.dumps({
            "status": "report_ready",
            "message": "Báo cáo đã tạo xong",
            "report": stage_a_output.model_dump(),
        }) + "\n"

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
    """Main research endpoint - POST request"""
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
