"""
Main Entry Point - Stage A Market Research Agent
Complete pipeline execution
"""

import sys
import argparse
from rich import print as rprint
from rich.console import Console

from stage_a.02_environment import load_environment, setup_directories
from stage_a.03_llm_config import initialize_llm
from stage_a.04_data_models import StageAInput
from stage_a.05_clarification import clarify_user_prompt
from stage_a.06_planning import planner_chain
from stage_a.08_react import run_react_loop
from stage_a.09_evidence_processing import normalize_and_filter_evidence
from stage_a.10_synthesis import synthesize_stage_a_report
from stage_a.11_output_formatting import build_markdown_report, build_json_report
from stage_a.12_mongodb import MongoDBManager
from stage_a.13_flask_api import create_app
from stage_a.14_ngrok_tunnel import run_server


console = Console()


def run_pipeline(user_prompt: str, **kwargs):
    """Run complete research pipeline"""
    rprint("[bold cyan]🚀 STAGE A MARKET RESEARCH AGENT[/bold cyan]")
    rprint(f"[yellow]User Prompt: {user_prompt}[/yellow]\n")

    # Initialize
    config = load_environment()
    dirs = setup_directories()
    llm = initialize_llm()
    mongo = MongoDBManager(config.get("mongo_uri"))

    # Create input
    initial_input = StageAInput(
        user_prompt=user_prompt,
        nganh_hang=kwargs.get("industry", ""),
        thi_truong_muc_tieu=kwargs.get("market", ""),
        phan_khuc_quan_tam=kwargs.get("segments", []),
        doi_thu_seed=kwargs.get("competitors", []),
        khung_thoi_gian=kwargs.get("timeframe", "12 thang gan nhat"),
        muc_tieu_nghien_cuu=kwargs.get("objectives", []),
    )

    # Step 1: Clarification
    rprint("[bold yellow]STEP 1: Clarifying Input[/bold yellow]")
    clarification = clarify_user_prompt(llm, user_prompt, initial_input)
    research_input = clarification["clarified_input"]
    rprint(f"[green]✅ Input clarified[/green]")
    rprint(f"  - Industry: {research_input.nganh_hang}")
    rprint(f"  - Market: {research_input.thi_truong_muc_tieu}\n")

    # Step 2: Planning
    rprint("[bold yellow]STEP 2: Planning Research[/bold yellow]")
    plan = planner_chain(llm, research_input)
    rprint(f"[green]✅ Plan created with {len(plan.get('steps', []))} steps\n[/green]")

    # Step 3: ReAct Loop
    rprint("[bold yellow]STEP 3: Executing ReAct Loop[/bold yellow]")
    react_state = run_react_loop(llm, plan)
    rprint(f"[green]✅ Collected {len(react_state['evidence'])} evidence items\n[/green]")

    # Step 4: Evidence Processing
    rprint("[bold yellow]STEP 4: Processing Evidence[/bold yellow]")
    evidence_df = normalize_and_filter_evidence(react_state["evidence"])
    rprint(f"[green]✅ Filtered to {len(evidence_df)} quality items\n[/green]")

    # Step 5: Synthesis
    rprint("[bold yellow]STEP 5: Synthesizing Report[/bold yellow]")
    output = synthesize_stage_a_report(llm, research_input, evidence_df)
    rprint(f"[green]✅ Report synthesized with {len(output.citations)} citations\n[/green]")

    # Step 6: Format and Save
    rprint("[bold yellow]STEP 6: Formatting Output[/bold yellow]")
    
    # Save Markdown
    markdown_report = build_markdown_report(research_input, output)
    markdown_path = dirs["output"] / f"report_{user_prompt[:20].replace(' ', '_')}.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    rprint(f"[green]✅ Markdown saved: {markdown_path}[/green]")

    # Save JSON
    metadata = {
        "plan": plan,
        "react_summary": {
            "tool_calls": react_state.get("tool_calls", 0),
        }
    }
    json_report = build_json_report(research_input, output, metadata)
    json_path = dirs["output"] / f"report_{user_prompt[:20].replace(' ', '_')}.json"
    import json
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    rprint(f"[green]✅ JSON saved: {json_path}[/green]")

    # Save to MongoDB
    if mongo:
        metadata["input"] = research_input.model_dump()
        mongodb_id = mongo.save_report(metadata, output)
        rprint(f"[green]✅ MongoDB ID: {mongodb_id}[/green]")

    rprint("\n[bold green]✅ PIPELINE COMPLETED SUCCESSFULLY[/bold green]")
    
    mongo.close() if mongo else None
    return output


def run_server_mode(port: int = 5000, use_ngrok: bool = True):
    """Run Flask server mode"""
    rprint("[bold cyan]🚀 STARTING FLASK API SERVER[/bold cyan]")
    
    app = create_app()
    run_server(app, port=port, use_ngrok=use_ngrok)


def main():
    parser = argparse.ArgumentParser(description="Stage A Market Research Agent")
    parser.add_argument("mode", nargs="?", default="pipeline", 
                       choices=["pipeline", "server"],
                       help="Execution mode: pipeline or server")
    parser.add_argument("-p", "--prompt", type=str, 
                       help="Research prompt (for pipeline mode)")
    parser.add_argument("--industry", type=str, default="",
                       help="Industry domain")
    parser.add_argument("--market", type=str, default="",
                       help="Target market")
    parser.add_argument("--port", type=int, default=5000,
                       help="Flask server port")
    parser.add_argument("--no-ngrok", action="store_true",
                       help="Disable ngrok tunnel")

    args = parser.parse_args()

    try:
        if args.mode == "server":
            run_server_mode(port=args.port, use_ngrok=not args.no_ngrok)
        else:  # pipeline mode
            if not args.prompt:
                rprint("[red]✗ Error: Prompt required for pipeline mode[/red]")
                print(parser.format_help())
                sys.exit(1)
            
            run_pipeline(
                args.prompt,
                industry=args.industry,
                market=args.market
            )

    except KeyboardInterrupt:
        rprint("\n[yellow]⚠️ Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        rprint(f"[red]✗ Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
