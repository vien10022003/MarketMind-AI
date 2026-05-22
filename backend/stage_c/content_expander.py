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
        # Import helper function
        from stage_a.tool_definitions import build_messages_from_history
        
        title = brief.get("title", "")
        caption = brief.get("caption", "")
        image_prompt = brief.get("image_prompt", "")
        content_type = brief.get("content_type", "")
        pillar = brief.get("pillar", "")
        product_context = brief.get("product_context", "")
        
        prompt = f"""Dựa vào bản tóm tắt bài đăng (Content Brief) dưới đây, hãy hoàn thiện bài đăng quảng bá sản phẩm.
Trả về với format sau:

** Nội Dung Bài Đăng **
[Nội dung bài đăng chi tiết, hấp dẫn, có emoji, quảng bá sản phẩm]

** Prompt Ảnh **
[Prompt ảnh liên quan đến sản phẩm bằng tiếng Anh]

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
            system_message="Bạn là một chuyên gia tạo nội dung Discord và prompt ảnh chuyên nghiệp. Hãy hoàn thiện nội dung theo format chỉ định.",
            max_new_tokens=800,
            temperature=0.7
        )
        
        # Parse output dựa trên pattern ** .... **
        output_clean = output.strip()
        
        new_caption = ""
        new_image_prompt = ""
        
        # Split bằng ** để lấy các phần
        parts = output_clean.split("**")
        # Format: ['...', 'tiêu đề 1', 'content 1', 'tiêu đề 2', 'content 2', ...]
        
        if len(parts) >= 5:
            # parts[2] = nội dung sau tiêu đề thứ nhất
            # parts[4] = nội dung sau tiêu đề thứ hai
            new_caption = parts[2].strip()
            new_image_prompt = parts[4].strip()
            print("aaaaa")
            print("new_caption")
            print(new_caption)
            print("new_image_prompt")
            print(new_image_prompt)
        
        # Cập nhật brief
        expanded_brief = brief.copy()
        if new_caption and len(new_caption) > 10:
            expanded_brief["caption"] = new_caption
        if new_image_prompt and len(new_image_prompt) > 5:
            expanded_brief["image_prompt"] = new_image_prompt
        
        rprint(f"[green]✅ Hoàn thiện nội dung thành công cho: {title}[/green]")
        return expanded_brief
        
    except Exception as e:
        rprint(f"[red]❌ Lỗi khi mở rộng nội dung: {e}[/red]")
        rprint(f"[yellow]LLM Output: {output}[/yellow]")
        print("brief")
        print(brief)
        return brief
