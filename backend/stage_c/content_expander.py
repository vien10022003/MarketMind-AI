import json
from typing import Optional, List, Dict, Any
from rich import print as rprint

def expand_content_brief(llm, brief: dict, conversation_history: Optional[List[Dict[str, str]]] = None) -> dict:
    """
    Sử dụng LLM để hoàn thiện Content Brief thành nội dung chi tiết và prompt ảnh chuyên nghiệp.
    Trả về một bản copy của brief đã được cập nhật 'caption' và 'image_prompt'.
    """
    if not llm:
        rprint("[yellow]⚠️ Không có LLM. Bỏ qua bước mở rộng nội dung.[/yellow]")
        return brief
        
    title = brief.get("title", "")
    caption = brief.get("caption", "")
    image_prompt = brief.get("image_prompt", "")
    content_type = brief.get("content_type", "")
    pillar = brief.get("pillar", "")
    product_context = brief.get("product_context", "")
    
    prompt = f"""Dựa vào bản tóm tắt bài đăng (Content Brief) dưới đây, hãy hoàn thiện bài đăng quảng bá sản phẩm:
Sản phẩm/Yêu cầu quảng cáo: {product_context}
1. Viết một bài đăng (caption) chi tiết, hấp dẫn, có sử dụng emoji phù hợp, văn phong tự nhiên để đăng lên Discord. Nội dung này dùng để thuyết phục và tương tác với người đọc, nhấn mạnh vào sản phẩm/yêu cầu đã nêu.
2. Viết một câu lệnh (image_prompt) sinh ảnh chuyên nghiệp bằng TIẾNG ANH (chỉ tiếng Anh), gồm các từ khóa miêu tả chi tiết, rõ nét, phong cách, ánh sáng, phân tách bằng dấu phẩy. Ảnh phải mang phong cách phù hợp với sản phẩm.

--- Bản tóm tắt ---
Tiêu đề: {title}
Thể loại: {content_type}
Chủ đề chính: {pillar}
Tóm tắt nội dung: {caption}
Ý tưởng ảnh cơ bản: {image_prompt}

--- Yêu cầu kết quả ---
Trả về kết quả ở định dạng JSON chuẩn. Không có markdown text dư thừa, không có chú thích thêm:
{{
    "expanded_caption": "<Nội dung bài đăng Discord hoàn chỉnh>",
    "expanded_image_prompt": "<Prompt ảnh tiếng Anh chi tiết, phân cách bằng dấu phẩy>"
}}"""
    
    try:
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho: {title}[/cyan]")
        from stage_a.tool_definitions import build_messages_from_history
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho1: {title}[/cyan]")
        messages = build_messages_from_history(prompt, conversation_history, max_history=2)
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho2: {title}[/cyan]")
        output = llm.generate(
            messages=messages,
            system_message="Ban la mot chuyen gia viet noi dung Marketing xuất sắc trên nền tảng Discord va mot chuyen gia viet prompt sinh anh chuyên nghiệp.",
            max_new_tokens=800,
            temperature=0.7
        )
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho3: {title}[/cyan]")
        # Xử lý parse JSON an toàn
        output_clean = output.strip()
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho4: {title}[/cyan]")
        if "```json" in output_clean:
            rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho5: {title}[/cyan]")
            output_clean = output_clean.split("```json")[1].split("```")[0].strip()
        elif "```" in output_clean:
            rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho6: {title}[/cyan]")
            output_clean = output_clean.split("```")[1].split("```")[0].strip()
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho7: {title}[/cyan]")
        data = json.loads(output_clean)
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho8: {title}[/cyan]")
        rprint(data)
        new_caption = data.get("expanded_caption", "")
        new_image_prompt = data.get("expanded_image_prompt", "")
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho9: {title}[/cyan]")
        # Cập nhật brief
        expanded_brief = brief.copy()
        if new_caption and len(new_caption) > 10:
            rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho10: {title}[/cyan]")
            expanded_brief["caption"] = new_caption
        if new_image_prompt and len(new_image_prompt) > 5:
            expanded_brief["image_prompt"] = new_image_prompt
            rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho11: {title}[/cyan]")
        rprint(f"[green]✅ Hoàn thiện nội dung thành công cho: {title}[/green]")
        return expanded_brief
        
    except json.JSONDecodeError:
        rprint(f"[red]❌ Lỗi parse JSON từ LLM khi mở rộng nội dung. Dùng bản gốc.[/red]")
        rprint(f"[yellow]LLM Output: {output}[/yellow]")
        return brief
    except Exception as e:
        rprint(f"[red]❌ Lỗi không xác định khi mở rộng nội dung: {e}[/red]")
        return brief
