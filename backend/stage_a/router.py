import json
from typing import Dict, Any
from rich import print as rprint

from .llm_config import LocalTextGenerator
from .clarification import extract_first_json_block

def classify_intent_and_respond(llm: LocalTextGenerator, user_prompt: str, conversation_history: list = None) -> Dict[str, Any]:
    """
    Classifies the user's prompt into one of three intents:
      - "chat": casual greeting or simple conversation
      - "knowledge": hard/complex question that may need web search for accurate answer
      - "research": marketing research / market analysis request
    
    If intent is "chat", generates a friendly response.
    
    Args:
        llm: The LLM text generator instance
        user_prompt: The current user prompt
        conversation_history: List of recent conversation turns [{"role": "user"|"assistant", "content": "..."}]
    
    Returns:
        Dict with keys: intent, response, reasoning
    """
    # Build conversation context string from history
    history_context = ""
    if conversation_history:
        history_parts = []
        for turn in conversation_history:
            role_label = "User" if turn.get("role") == "user" else "Assistant"
            history_parts.append(f"{role_label}: {turn.get('content', '')}")
        history_context = "\n".join(history_parts)

    prompt = f"""
Ban la mot he thong phan loai y dinh nguoi dung cho ung dung MarketMind AI.
Nhiem vu: Phan loai cau hoi cua nguoi dung vao MOT trong BA loai sau:

1. "chat" - Cau chao hoi, tro chuyen don gian, cam on, hoi ve ban than chatbot, cau hoi rat don gian ai cung biet.
   Vi du: "Xin chao", "Ban la ai?", "Cam on nhe", "Hom nay troi dep qua"

2. "knowledge" - Cau hoi can kien thuc chuyen sau, du kien cu the, thong tin moi nhat, so sanh phuc tap, giai thich khai niem kho.
   KHONG phai yeu cau nghien cuu marketing chien luoc. Day la cau hoi co the tra loi truc tiep hoac can tim kiem them.
   Vi du: "GDP Viet Nam 2024 la bao nhieu?", "So sanh React va Vue", "Xu huong AI moi nhat la gi?", "Giai thich blockchain"

3. "research" - Yeu cau phan tich thi truong, lap chien luoc marketing, nghien cuu doi thu canh tranh, phan tich nganh hang, 
   nghien cuu phan khuc khach hang, bao cao thi truong toan dien.
   Vi du: "Phan tich thi truong ca phe Viet Nam", "Lap chien luoc marketing cho san pham moi", "Nghien cuu doi thu trong nganh my pham"

Neu la "chat", hay dua ra cau tra loi than thien. Su dung lich su hoi thoai (neu co) de tra loi phu hop.
Neu la "knowledge" hoac "research", de response la chuoi rong.

{f"Lich su hoi thoai gan day:{chr(10)}{history_context}{chr(10)}" if history_context else ""}User prompt: "{user_prompt}"

YEU CAU (Chi tra ve JSON, khong van ban):
{{
  "intent": "chat" | "knowledge" | "research",
  "response": "Cau tra loi neu intent la 'chat', nguoc lai de trong ''",
  "reasoning": "Ly do ngan gon tai sao phan loai nhu vay"
}}
"""
    raw = llm.generate(prompt, max_new_tokens=400)
    block = extract_first_json_block(raw)
    
    rprint(f"[cyan]--- Intent Classification raw ---[/cyan]")
    rprint(raw)
    result = {
        "intent": "research",
        "response": "",
        "reasoning": ""
    }
    
    if block:
        try:
            parsed = json.loads(block)
            # Validate intent value
            valid_intents = {"chat", "knowledge", "research"}
            if parsed.get("intent") not in valid_intents:
                parsed["intent"] = "research"
            result.update(parsed)
            rprint(f"[green]✅ Intent Classification completed: {result.get('intent')} — {result.get('reasoning', '')}[/green]")
        except json.JSONDecodeError:
            rprint("[yellow]⚠️ Intent Classification JSON parse failed, defaulting to research[/yellow]")
    
    return result
