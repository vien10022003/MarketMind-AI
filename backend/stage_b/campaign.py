"""
Campaign Module - Stage B
Campaign Plan creation and Content Brief generation for Discord.
"""

import json
import re
from typing import List, Generator, Optional, Dict, Any
from rich import print as rprint

from .data_models_b import (
    SWOTAnalysis, USPResult, BuyerPersona, ContentPillar,
    ScheduleEntry, CampaignPlan, ContentBrief, StageBInput, StageBOutput,
)
from .strategy import (
    _extract_json,
    generate_swot_analysis, extract_usp, refine_persona, define_content_pillars,
)


def _stringify_field(value):
    """
    Convert list/dict/nested structures to string.
    Handles cases where LLM returns list or dict instead of string.
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, list):
        # Join list items with newline
        return "\n".join([str(item) for item in value])
    elif isinstance(value, dict):
        # Convert dict to readable format
        if len(value) == 1 and 'description' in value:
            return str(value.get('description', ''))
        else:
            return json.dumps(value, ensure_ascii=False)
    else:
        return str(value)


def create_campaign_plan(
    llm,
    pillars: List[ContentPillar],
    persona: BuyerPersona,
    stage_a_input: dict,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> CampaignPlan:
    """Create a 7-day campaign plan with schedule."""
    rprint("[yellow][STAGE B] Creating Campaign Plan...[/yellow]")

    pillar_names = [f"{p.emoji} {p.name}" for p in pillars]
    product_context = stage_a_input.get('user_prompt', stage_a_input.get('nganh_hang', 'Sản phẩm/Dịch vụ'))

    json_example = '{"duration_days":7,"posting_frequency":"1 post/ngay","campaign_goal":"Muc tieu chien dich lien quan den san pham","content_types":["tip","infographic","meme"],"schedule":[{"day":1,"time":"19:00","content_type":"tip","pillar_name":"Ten pillar"}]}'
    
    prompt = f"""Tao ke hoach chien dich 7 ngay xoay quanh viec quang ba san pham nay.

San pham/Yeu cau: {product_context}
Content Pillars: {', '.join(pillar_names)}
Persona: {persona.name} ({persona.age_range})
Content types ua thich: {', '.join(persona.preferred_content_types[:4])}

Tra ve CHINH XAC JSON:
{json_example}
Tao 7 schedule entries (1 moi ngay). JSON thuan tuy."""

    from stage_a.tool_definitions import build_messages_from_history
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    raw = llm.generate(
        messages=messages,
        system_message="Ban la chuyen gia lap ke hoach chien dich Discord. Tao ke hoach chien dich 7 ngay xoay quanh viec quang ba san pham.",
        max_new_tokens=600
    )
    data = _extract_json(raw)

    if data and "schedule" in data:
        schedule = []
        for s in data["schedule"][:7]:
            schedule.append(ScheduleEntry(
                day=s.get("day", len(schedule) + 1),
                time=s.get("time", "19:00"),
                content_type=s.get("content_type", "tip"),
                pillar_name=s.get("pillar_name", pillars[0].name if pillars else ""),
            ))
        result = CampaignPlan(
            duration_days=data.get("duration_days", 7),
            posting_frequency=data.get("posting_frequency", "1 post/ngày"),
            content_types=data.get("content_types", ["tip", "infographic"]),
            schedule=schedule,
            campaign_goal=data.get("campaign_goal", "Tăng nhận diện thương hiệu"),
        )
    else:
        rprint("[red]⚠️ Campaign plan parse failed, using defaults[/red]")
        schedule = []
        for day in range(1, 8):
            pillar = pillars[(day - 1) % len(pillars)] if pillars else ContentPillar(name="General")
            schedule.append(ScheduleEntry(
                day=day, time="19:00",
                content_type=persona.preferred_content_types[(day - 1) % max(1, len(persona.preferred_content_types))] if persona.preferred_content_types else "tip",
                pillar_name=pillar.name,
            ))
        result = CampaignPlan(
            duration_days=7,
            posting_frequency="1 post/ngày",
            content_types=persona.preferred_content_types[:4] or ["tip", "infographic"],
            schedule=schedule,
            campaign_goal="Tăng nhận diện thương hiệu trên Discord",
        )

    rprint(f"[green]✅ Campaign Plan: {result.duration_days} days, {len(result.schedule)} posts[/green]")
    return result


def generate_content_briefs(
    llm,
    campaign_plan: CampaignPlan,
    pillars: List[ContentPillar],
    persona: BuyerPersona,
    usp: USPResult,
    stage_a_input: dict,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> List[ContentBrief]:
    """Generate content briefs for each scheduled post."""
    rprint("[yellow][STAGE B] Generating Content Briefs...[/yellow]")
    product_context = stage_a_input.get('user_prompt', stage_a_input.get('nganh_hang', 'Sản phẩm/Dịch vụ'))

    briefs = []
    colors = [0x57F287, 0x5865F2, 0xFEE75C, 0xED4245, 0xEB459E, 0x3498DB, 0xE67E22]

    from stage_a.tool_definitions import build_messages_from_history
    for entry in campaign_plan.schedule:
        # Find pillar details
        pillar_detail = next((p for p in pillars if p.name == entry.pillar_name), None)
        pillar_desc = pillar_detail.description if pillar_detail else entry.pillar_name
        topics = pillar_detail.example_topics if pillar_detail else []
        topics_text = ', '.join(topics[:2]) if topics else entry.content_type

        json_example = '{"title":"Tieu de bai dang (ngan gon, hap dan)","caption":"Noi dung caption day du cho Discord embed (2-4 cau, co emoji) va nhac den san pham hoac quang cao loi ich","image_prompt":"English prompt for AI image generation (descriptive, specific, related to the topic and product style)"}'
        
        prompt = f"""Tao content brief cho 1 bai dang Discord de quang ba san pham.

San pham/Yeu cau: {product_context}
Ngay: {entry.day}, Gio: {entry.time}
Pillar: {entry.pillar_name} - {pillar_desc}
Content type: {entry.content_type}
Chu de goi y: {topics_text}
Persona: {persona.name} ({persona.age_range})
USP: {usp.usp_statement}

Tra ve CHINH XAC JSON:
{json_example}
JSON thuan tuy."""

        messages = build_messages_from_history(prompt, conversation_history, max_history=2)
        raw = llm.generate(
            messages=messages,
            system_message="Ban la copywriter cho Discord. Tao content brief cho 1 bai dang Discord de quang ba san pham.",
            max_new_tokens=400
        )
        data = _extract_json(raw)

        if data:
            brief = ContentBrief(
                title=data.get("title", f"Bài đăng ngày {entry.day}"),
                caption=_stringify_field(data.get("caption", f"Nội dung về {entry.pillar_name}")),
                image_prompt=_stringify_field(data.get("image_prompt", f"Modern marketing visual for {entry.content_type}")),
                content_type=entry.content_type,
                pillar=entry.pillar_name,
                scheduled_day=entry.day,
                scheduled_time=entry.time,
                status="pending",
                embed_color=colors[(entry.day - 1) % len(colors)],
                product_context=product_context,
            )
        else:
            brief = ContentBrief(
                title=f"{entry.pillar_name} - Ngày {entry.day}",
                caption=f"✨ {pillar_desc}\n\n💡 {usp.usp_statement}",
                image_prompt=f"Modern clean marketing visual, {entry.content_type} style, professional design",
                content_type=entry.content_type,
                pillar=entry.pillar_name,
                scheduled_day=entry.day,
                scheduled_time=entry.time,
                status="pending",
                embed_color=colors[(entry.day - 1) % len(colors)],
                product_context=product_context,
            )

        briefs.append(brief)
        rprint(f"  📝 Brief {len(briefs)}: {brief.title[:50]}")

    rprint(f"[green]✅ Content Briefs: {len(briefs)} briefs generated[/green]")
    return briefs


def run_stage_b_pipeline(llm, stage_b_input: StageBInput) -> Generator[dict, None, None]:
    """
    Run the complete Stage B pipeline as a generator (for streaming).
    Yields progress events and final strategy document.
    """
    report = stage_b_input.stage_a_report
    input_cfg = stage_b_input.stage_a_input

    yield {"status": "stage_b_starting", "message": "🚀 Bắt đầu xây dựng chiến lược marketing..."}

    # Step 1: SWOT
    yield {"status": "progress", "message": "📊 Đang phân tích SWOT..."}
    swot = generate_swot_analysis(llm, report, input_cfg)
    yield {
        "status": "swot_completed",
        "message": f"✅ SWOT hoàn tất: {len(swot.strengths)}S/{len(swot.weaknesses)}W/{len(swot.opportunities)}O/{len(swot.threats)}T",
        "swot": swot.model_dump(),
    }

    # Step 2: USP
    yield {"status": "progress", "message": "🎯 Đang rút trích USP..."}
    usp = extract_usp(llm, report, swot, input_cfg)
    yield {
        "status": "usp_completed",
        "message": f"✅ USP: {usp.usp_statement[:80]}",
        "usp": usp.model_dump(),
    }

    # Step 3: Persona
    yield {"status": "progress", "message": "👤 Đang xây dựng Buyer Persona..."}
    persona = refine_persona(llm, report, input_cfg, usp)
    yield {
        "status": "persona_completed",
        "message": f"✅ Persona: {persona.name}",
        "persona": persona.model_dump(),
    }

    # Step 4: Content Pillars
    yield {"status": "progress", "message": "📌 Đang xác định Content Pillars..."}
    pillars = define_content_pillars(llm, report, persona, usp, input_cfg)
    yield {
        "status": "pillars_completed",
        "message": f"✅ {len(pillars)} Content Pillars xác định",
        "content_pillars": [p.model_dump() for p in pillars],
    }

    # Step 5: Campaign Plan
    yield {"status": "progress", "message": "📅 Đang lập kế hoạch chiến dịch..."}
    campaign_plan = create_campaign_plan(llm, pillars, persona, input_cfg)
    yield {
        "status": "campaign_plan_completed",
        "message": f"✅ Kế hoạch: {campaign_plan.duration_days} ngày, {len(campaign_plan.schedule)} bài",
        "campaign_plan": campaign_plan.model_dump(),
    }

    # Step 6: Content Briefs
    yield {"status": "progress", "message": "📝 Đang tạo Content Briefs..."}
    briefs = generate_content_briefs(llm, campaign_plan, pillars, persona, usp, input_cfg)
    yield {
        "status": "briefs_generated",
        "message": f"✅ {len(briefs)} content briefs đã tạo",
        "content_briefs": [b.model_dump() for b in briefs],
    }

    # Final output
    stage_b_output = StageBOutput(
        swot=swot, usp=usp, persona=persona,
        content_pillars=pillars, campaign_plan=campaign_plan,
        content_briefs=briefs,
    )

    yield {
        "status": "stage_b_completed",
        "message": "🎉 Chiến lược marketing hoàn tất! Vui lòng xem xét và phê duyệt các content briefs.",
        "strategy": stage_b_output.model_dump(),
    }
