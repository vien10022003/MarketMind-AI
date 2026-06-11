import json
from typing import Optional, List, Dict, Any
from rich import print as rprint

def expand_content_brief(llm, brief: dict, conversation_history: Optional[List[Dict[str, str]]] = None) -> dict:
    """
    Sử dụng LLM để hoàn thiện Content Brief thành nội dung chi tiết và prompt ảnh chuyên nghiệp.
    
    Xử lý khác nhau tùy theo LLM provider:
    - Gemini: dùng 1 prompt để tạo cả caption và image_prompt cùng lúc
    - LocalLlama: tách thành 2 prompt riêng biệt (1 cho caption, 1 cho image_prompt)
    
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
        
        # Xác định provider
        provider_name = llm.provider_name if hasattr(llm, 'provider_name') else "unknown"
        is_local_llama = provider_name == "local_llama"
        
        rprint(f"[cyan]🧠 Đang dùng {provider_name} hoàn thiện nội dung cho: {title}[/cyan]")
        
        expanded_brief = brief.copy()
        new_caption = ""
        new_image_prompt = ""
        
        if True:  # For simplicity, we will use the 2-prompt approach for all providers to ensure better quality and control
            # ─── LOCAL LLAMA: 2 Prompts riêng biệt ───
            rprint(f"[dim]Sử dụng 2 prompts riêng cho LocalLlama[/dim]")
            
            # Prompt 1: Tạo nội dung bài đăng
            caption_prompt = f"""Dựa vào bản tóm tắt bài đăng dưới đây, hãy tạo nội dung bài đăng Discord chi tiết, hấp dẫn, có emoji để quảng bá sản phẩm.

Sản phẩm/Yêu cầu: {product_context}
Tiêu đề: {title}
Thể loại: {content_type}
Chủ đề: {pillar}
Tóm tắt: {caption}

Hãy tạo nội dung bài đăng chi tiết, đánh động, có emoji, quảng bá sản phẩm."""
            
            messages = build_messages_from_history(caption_prompt, conversation_history, max_history=2)
            caption_output = llm.generate(
                messages=messages,
                system_message="Bạn là chuyên gia tạo nội dung Discord. Hãy tạo nội dung quảng bá sản phẩm chi tiết, hấp dẫn, có emoji.",
                max_new_tokens=500,
                temperature=0.7
            )
            new_caption = caption_output.strip()
            
            # Prompt 2: Tạo image prompt (English)
            image_prompt_text = f"""Based on the Discord post content below, create a professional English image generation prompt for Discord.

Product: {product_context}
Post Content: {new_caption}

Create a concise, professional image generation prompt in English that clearly describes the product and desired visual style. The prompt MUST be under 70 words."""
            
            messages = build_messages_from_history(image_prompt_text, conversation_history, max_history=2)
            image_prompt_output = llm.generate(
                messages=messages,
                system_message="You are an expert at creating image generation prompts. Generate a professional English prompt that is concise and clear.",
                max_new_tokens=75,  # Keep under 77 token limit for image model
                temperature=0.7
            )
            new_image_prompt = image_prompt_output.strip()
#         else:
#             # ─── GEMINI & Others: 1 Prompt kết hợp ───
#             rprint(f"[dim]Sử dụng 1 prompt kết hợp cho {provider_name}[/dim]")
            
#             prompt = f"""Dựa vào bản tóm tắt bài đăng (Content Brief) dưới đây, hãy hoàn thiện bài đăng quảng bá sản phẩm.
# Trả về với format sau:

# ** Nội Dung Bài Đăng **
# [Nội dung bài đăng chi tiết, hấp dẫn, có emoji, quảng bá sản phẩm]

# ** Image Prompt **
# [Image generation prompt in English for product-focused photos. CRITICAL: MUST be under 70 words (max 77 tokens)]

# Sản phẩm/Yêu cầu quảng cáo: {product_context}

# --- Bản tóm tắt ---
# Tiêu đề: {title}
# Thể loại: {content_type}
# Chủ đề chính: {pillar}
# Tóm tắt nội dung: {caption}
# Ý tưởng ảnh cơ bản: {image_prompt}"""
            
#             messages = build_messages_from_history(prompt, conversation_history, max_history=2)
#             output = llm.generate(
#                 messages=messages,
#                 system_message="Bạn là một chuyên gia tạo nội dung Discord và prompt ảnh chuyên nghiệp. Hãy hoàn thiện nội dung theo format chỉ định.",
#                 max_new_tokens=800,
#                 temperature=0.7
#             )
            
#             # Parse output dựa trên pattern ** .... **
#             output_clean = output.strip()
            
#             # Split bằng ** để lấy các phần
#             parts = output_clean.split("**")
#             # Format: ['...', 'tiêu đề 1', 'content 1', 'tiêu đề 2', 'content 2', ...]
            
#             if len(parts) >= 5:
#                 # parts[2] = nội dung sau tiêu đề thứ nhất
#                 # parts[4] = nội dung sau tiêu đề thứ hai
#                 new_caption = parts[2].strip()
#                 new_image_prompt = parts[4].strip()
        
        # Cập nhật brief với kết quả mới
        if new_caption and len(new_caption) > 10:
            expanded_brief["caption"] = new_caption
        if new_image_prompt and len(new_image_prompt) > 5:
            expanded_brief["image_prompt"] = new_image_prompt
        
        rprint(f"[green]✅ Hoàn thiện nội dung thành công cho: {title}[/green]")
        return expanded_brief
        
    except Exception as e:
        rprint(f"[red]❌ Lỗi khi mở rộng nội dung: {e}[/red]")
        import traceback
        traceback.print_exc()
        return brief
