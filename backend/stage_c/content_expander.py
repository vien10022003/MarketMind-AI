import json
from typing import Optional, List, Dict, Any
from rich import print as rprint

def expand_content_brief(llm, brief: dict, conversation_history: Optional[List[Dict[str, str]]] = None) -> dict:
    """
    Sử dụng LLM để hoàn thiện Content Brief thành nội dung chi tiết và prompt ảnh chuyên nghiệp.
    Sử dụng tool definitions để đảm bảo format JSON đúng.
    Trả về một bản copy của brief đã được cập nhật 'caption' và 'image_prompt'.
    """
    if not llm:
        rprint("[yellow]⚠️ Không có LLM. Bỏ qua bước mở rộng nội dung.[/yellow]")
        return brief
    
    try:
        # Import tool definitions
        from stage_a.tool_definitions import CONTENT_EXPANSION_TOOLS, SYSTEM_MESSAGE_CONTENT_EXPANDER, build_messages_from_history
        
        title = brief.get("title", "")
        caption = brief.get("caption", "")
        image_prompt = brief.get("image_prompt", "")
        content_type = brief.get("content_type", "")
        pillar = brief.get("pillar", "")
        product_context = brief.get("product_context", "")
        
        prompt = f"""Dựa vào bản tóm tắt bài đăng (Content Brief) dưới đây, hãy hoàn thiện bài đăng quảng bá sản phẩm:
Sản phẩm/Yêu cầu quảng cáo: {product_context}

--- Bản tóm tắt ---
Tiêu đề: {title}
Thể loại: {content_type}
Chủ đề chính: {pillar}
Tóm tắt nội dung: {caption}
Ý tưởng ảnh cơ bản: {image_prompt}"""
        
        rprint(f"[cyan]🧠 Đang dùng LLM hoàn thiện nội dung cho: {title}[/cyan]")
        
        messages = build_messages_from_history(prompt, conversation_history, max_history=2)
        
        output = llm.generate(
            messages=messages,
            system_message=SYSTEM_MESSAGE_CONTENT_EXPANDER,
            tools=CONTENT_EXPANSION_TOOLS,  # Pass tool definition to ensure correct format
            max_new_tokens=800,
            temperature=0.7
        )
        
        # Xử lý parse JSON an toàn
        output_clean = output.strip()
        if "```json" in output_clean:
            output_clean = output_clean.split("```json")[1].split("```")[0].strip()
        elif "```" in output_clean:
            output_clean = output_clean.split("```")[1].split("```")[0].strip()
        
        data = json.loads(output_clean)
        
        new_caption = data.get("expanded_caption", "")
        new_image_prompt = data.get("expanded_image_prompt", "")
        
        # Cập nhật brief
        expanded_brief = brief.copy()
        if new_caption and len(new_caption) > 10:
            expanded_brief["caption"] = new_caption
        if new_image_prompt and len(new_image_prompt) > 5:
            expanded_brief["image_prompt"] = new_image_prompt
        
        rprint(f"[green]✅ Hoàn thiện nội dung thành công cho: {title}[/green]")
        return expanded_brief
        
    except json.JSONDecodeError:
        rprint(f"[red]❌ Lỗi parse JSON từ LLM khi mở rộng nội dung. Dùng bản gốc.[/red]")
        rprint(f"[yellow]LLM Output: {output}[/yellow]")
        return brief
    except Exception as e:
        rprint(f"[red]❌ Lỗi không xác định khi mở rộng nội dung: {e}[/red]")
        return brief
