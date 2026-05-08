"""
Strategy Module - Stage B
LLM-powered strategy generation: SWOT, USP, Persona, Content Pillars
"""

import json
import re
from typing import List, Optional, Dict, Any
from rich import print as rprint

from .data_models_b import (
    SWOTAnalysis, USPResult, BuyerPersona, ContentPillar,
)


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM output, handling markdown code blocks."""
    code_block = re.search(r'```(?:json)?\s*\n?(.*?)```', text, re.DOTALL)
    if code_block:
        text = code_block.group(1).strip()
    brace_start = text.find('{')
    if brace_start == -1:
        return {}
    depth = 0
    for i in range(brace_start, len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[brace_start:i+1])
                except json.JSONDecodeError:
                    break
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {}


def generate_swot_analysis(llm, stage_a_report: dict, stage_a_input: dict, conversation_history: Optional[List[Dict[str, str]]] = None) -> SWOTAnalysis:
    """Generate SWOT analysis from Stage A research report."""
    rprint("[yellow][STAGE B] Generating SWOT Analysis...[/yellow]")
    product_context = stage_a_input.get('user_prompt', stage_a_input.get('nganh_hang', 'Sản phẩm/Dịch vụ'))
    report_ctx = (
        f"Tong quan: {stage_a_report.get('tong_quan_thi_truong', '')[:600]}\n"
        f"Doi thu: {stage_a_report.get('phan_tich_doi_thu', '')[:600]}\n"
        f"Xu huong: {stage_a_report.get('xu_huong_nganh', '')[:600]}\n"
        f"Insight: {stage_a_report.get('phan_khuc_va_insight_khach_hang', '')[:600]}"
    )
    prompt = f"""Dua tren bao cao nghien cuu va thong tin san pham, tao phan tich SWOT.
San pham/Yeu cau: {product_context}
Nganh: {stage_a_input.get('nganh_hang', 'N/A')}
Thi truong: {stage_a_input.get('thi_truong_muc_tieu', 'N/A')}
Bao cao:
{report_ctx}

Tra ve CHINH XAC JSON (KHONG text khac):
{{"strengths":["s1","s2","s3"],"weaknesses":["w1","w2","w3"],"opportunities":["o1","o2","o3"],"threats":["t1","t2","t3"]}}
Moi muc 3-5 diem cu the. JSON thuan tuy."""

    from .tool_definitions import build_messages_from_history
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    raw = llm.generate(
        messages=messages,
        system_message="Ban la chuyen gia marketing chien luoc. Tao phan tich SWOT dua tren bao cao.",
        max_new_tokens=600
    )
    data = _extract_json(raw)
    if data:
        result = SWOTAnalysis(
            strengths=data.get("strengths", ["Cần thêm dữ liệu"]),
            weaknesses=data.get("weaknesses", ["Cần thêm dữ liệu"]),
            opportunities=data.get("opportunities", ["Cần thêm dữ liệu"]),
            threats=data.get("threats", ["Cần thêm dữ liệu"]),
        )
    else:
        rprint("[red]⚠️ SWOT parse failed, using defaults[/red]")
        result = SWOTAnalysis(
            strengths=["Thị trường tăng trưởng", "Nhu cầu cao", "Cơ hội số hóa"],
            weaknesses=["Cạnh tranh gay gắt", "Chi phí marketing cao", "Thiếu nhận diện"],
            opportunities=["Xu hướng mới", "Kênh Discord tiềm năng", "Phân khúc ngách"],
            threats=["Đối thủ lớn", "Biến động thị trường", "Thay đổi hành vi"],
        )
    rprint(f"[green]✅ SWOT: {len(result.strengths)}S/{len(result.weaknesses)}W/{len(result.opportunities)}O/{len(result.threats)}T[/green]")
    return result


def extract_usp(llm, stage_a_report: dict, swot: SWOTAnalysis, stage_a_input: dict, conversation_history: Optional[List[Dict[str, str]]] = None) -> USPResult:
    """Extract Unique Selling Proposition based on research + SWOT."""
    rprint("[yellow][STAGE B] Extracting USP...[/yellow]")
    product_context = stage_a_input.get('user_prompt', stage_a_input.get('nganh_hang', 'Sản phẩm/Dịch vụ'))
    prompt = f"""Rut ra USP tu SWOT, bao cao va dac diem san pham.
San pham/Yeu cau: {product_context}
Diem manh: {', '.join(swot.strengths[:3])}
Co hoi: {', '.join(swot.opportunities[:3])}
Tong quan: {stage_a_report.get('tong_quan_thi_truong', '')[:400]}

Tra ve CHINH XAC JSON (KHONG text khac):
{{"usp_statement":"Tuyen bo USP 1-2 cau","supporting_points":["p1","p2","p3"],"competitive_advantage":"Loi the canh tranh"}}
JSON thuan tuy."""

    from .tool_definitions import build_messages_from_history
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    raw = llm.generate(
        messages=messages,
        system_message="Ban la chuyen gia dinh vi thuong hieu. Rut ra USP tu SWOT va bao cao.",
        max_new_tokens=400
    )
    data = _extract_json(raw)
    if data:
        result = USPResult(
            usp_statement=data.get("usp_statement", "Giải pháp tối ưu cho thị trường"),
            supporting_points=data.get("supporting_points", []),
            competitive_advantage=data.get("competitive_advantage", ""),
        )
    else:
        rprint("[red]⚠️ USP parse failed, using defaults[/red]")
        result = USPResult(
            usp_statement="Giải pháp tối ưu và sáng tạo cho thị trường mục tiêu",
            supporting_points=["Dựa trên dữ liệu thực", "Tận dụng xu hướng mới", "Giá trị vượt trội"],
            competitive_advantage="Kết hợp AI với hiểu biết thị trường sâu sắc",
        )
    rprint(f"[green]✅ USP: {result.usp_statement[:60]}...[/green]")
    return result


def _ensure_string(value, default: str = "") -> str:
    """Convert any value to string, handling dict/list types."""
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        # Convert dict to comma-separated values
        return ", ".join(str(v) for v in value.values() if v)
    elif isinstance(value, list):
        return ", ".join(str(v) for v in value if v)
    else:
        return str(value) if value else default


def refine_persona(llm, stage_a_report: dict, stage_a_input: dict, usp: USPResult, conversation_history: Optional[List[Dict[str, str]]] = None) -> BuyerPersona:
    """Refine buyer persona for Discord marketing."""
    rprint("[yellow][STAGE B] Refining Buyer Persona...[/yellow]")
    segments = stage_a_input.get('phan_khuc_quan_tam', [])
    segments_text = ', '.join(segments) if segments else 'Chưa xác định'

    product_context = stage_a_input.get('user_prompt', stage_a_input.get('nganh_hang', 'Sản phẩm/Dịch vụ'))
    prompt = f"""Tao persona cho chien dich Discord phu hop voi san pham nay.
San pham/Yeu cau: {product_context}
Nganh: {stage_a_input.get('nganh_hang', 'N/A')}
Thi truong: {stage_a_input.get('thi_truong_muc_tieu', 'N/A')}
Phan khuc: {segments_text}
USP: {usp.usp_statement}
Insight: {stage_a_report.get('phan_khuc_va_insight_khach_hang', '')[:400]}

Tra ve CHINH XAC JSON:
{{"name":"Ten persona","age_range":"18-25","interests":["i1","i2"],"pain_points":["p1","p2"],"discord_behavior":"Mo ta hanh vi Discord","preferred_content_types":["tips","memes"],"goals":["g1","g2"]}}
JSON thuan tuy."""

    from .tool_definitions import build_messages_from_history
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    raw = llm.generate(
        messages=messages,
        system_message="Ban la chuyen gia buyer persona cho Discord. Tao persona cho chien dich Discord.",
        max_new_tokens=500
    )
    data = _extract_json(raw)
    if data:
        result = BuyerPersona(
            name=_ensure_string(data.get("name"), "Khách hàng mục tiêu"),
            age_range=_ensure_string(data.get("age_range"), "20-35"),
            interests=data.get("interests", []) if isinstance(data.get("interests"), list) else [],
            pain_points=data.get("pain_points", []) if isinstance(data.get("pain_points"), list) else [],
            discord_behavior=_ensure_string(data.get("discord_behavior"), "Hoạt động trên Discord"),
            preferred_content_types=data.get("preferred_content_types", ["tips", "infographic"]) if isinstance(data.get("preferred_content_types"), list) else ["tips"],
            goals=data.get("goals", []) if isinstance(data.get("goals"), list) else [],
        )
    else:
        rprint("[red]⚠️ Persona parse failed, using defaults[/red]")
        result = BuyerPersona(
            name="Khách hàng - Digital Native", age_range="20-35",
            interests=["Công nghệ", "Mua sắm online", "Xu hướng mới"],
            pain_points=["Thiếu thông tin", "Quá nhiều lựa chọn"],
            discord_behavior="Tham gia nhiều server, đọc tin hàng ngày",
            preferred_content_types=["tips", "infographic", "deals"],
            goals=["Tìm sản phẩm tốt", "Tiết kiệm thời gian"],
        )
    rprint(f"[green]✅ Persona: {result.name} ({result.age_range})[/green]")
    return result


def define_content_pillars(llm, stage_a_report: dict, persona: BuyerPersona, usp: USPResult, stage_a_input: dict, conversation_history: Optional[List[Dict[str, str]]] = None) -> List[ContentPillar]:
    """Define 3-5 content pillars for the Discord campaign."""
    rprint("[yellow][STAGE B] Defining Content Pillars...[/yellow]")
    product_context = stage_a_input.get('user_prompt', stage_a_input.get('nganh_hang', 'Sản phẩm/Dịch vụ'))
    
    json_example = '{"pillars":[{"name":"Ten","description":"Mo ta","example_topics":["t1","t2"],"emoji":"📌"}]}'
    
    prompt = f"""Xac dinh 4 content pillars phu hop voi san pham va yeu cau quang cao sau:
San pham/Yeu cau: {product_context}

Persona: {persona.name} ({persona.age_range})
Content ua thich: {', '.join(persona.preferred_content_types[:3])}
USP: {usp.usp_statement}
Xu huong: {stage_a_report.get('xu_huong_nganh', '')[:300]}

Tra ve CHINH XAC JSON:
{json_example}
Tao 4 pillars. JSON thuan tuy."""

    from .tool_definitions import build_messages_from_history
    messages = build_messages_from_history(prompt, conversation_history, max_history=2)
    raw = llm.generate(
        messages=messages,
        system_message="Ban la chuyen gia content strategy cho Discord. Xac dinh content pillars phu hop.",
        max_new_tokens=600
    )
    data = _extract_json(raw)
    pillars = []
    if data and "pillars" in data:
        for p in data["pillars"][:5]:
            pillars.append(ContentPillar(
                name=p.get("name", "Content Pillar"),
                description=p.get("description", ""),
                example_topics=p.get("example_topics", []),
                emoji=p.get("emoji", "📌"),
            ))
    if not pillars:
        rprint("[red]⚠️ Pillars parse failed, using defaults[/red]")
        pillars = [
            ContentPillar(name="Kiến Thức Ngành", description="Chia sẻ kiến thức và xu hướng", example_topics=["Xu hướng mới", "Thống kê", "Phân tích"], emoji="📊"),
            ContentPillar(name="Tips & Tricks", description="Mẹo hữu ích", example_topics=["Cách chọn SP", "Mẹo tiết kiệm"], emoji="💡"),
            ContentPillar(name="Câu Chuyện", description="Xây dựng niềm tin", example_topics=["Behind the scenes", "Review"], emoji="❤️"),
            ContentPillar(name="Ưu Đãi", description="Khuyến mãi và sự kiện", example_topics=["Flash sale", "Giveaway"], emoji="🎁"),
        ]
    rprint(f"[green]✅ Content Pillars: {len(pillars)} pillars[/green]")
    return pillars
