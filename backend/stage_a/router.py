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

    prompt = f"""Ban la he thong phan loai y dinh nguoi dung. NHIEM VU: Phan loai prompt vao dung 1 trong 3 loai:

1. "chat" - Chao hoi, tro chuyen don gian, cam on, hoi ve chatbot, thong tin ai cung biet. Vi du: "Xin chao", "Ban la ai?"
2. "knowledge" - Khi bạn không có đủ thông tin như thông tin mới thay đổi liên tục, tin chi tiết cần độ chính xác cao. Vi du: "GDP 2024 la bao nhieu?"
3. "research" - Yeu cau marketing, phan tich thi truong, chien luoc marketing, nghien cuu doi thu canh tranh. Vi du: "Phan tich thi truong ca phe"

{f"Lich su:{chr(10)}{history_context}{chr(10)}" if history_context else ""}Prompt: "{user_prompt}"

RESPONSE DUNG DUNG DAY (CHI JSON, KHONG THEM GI):
{{"intent": "chat|knowledge|research", "response": "Chi dien neu chat", "reasoning": "Ly do"}}"""
    rprint(f"[blue]--- Intent Classification prompt ---[/blue]")
    rprint(prompt)
    raw = llm.generate(prompt, max_new_tokens=1000)
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
                rprint(f"[yellow]⚠️ Invalid intent '{parsed.get('intent')}', defaulting to research[/yellow]")
                parsed["intent"] = "research"
            result.update(parsed)
            rprint(f"[green]✅ Intent Classification: {result.get('intent')}[/green]")
        except json.JSONDecodeError as e:
            rprint(f"[yellow]⚠️ JSON parse failed: {e}, trying to extract intent from raw text[/yellow]")
            # Fallback: try to detect intent from raw response
            raw_lower = raw.lower()
            if "knowledge" in raw_lower and ("hoi" in raw_lower or "cau hoi" in raw_lower):
                result["intent"] = "knowledge"
            elif "research" in raw_lower or "chien luoc" in raw_lower or "phan tich thi truong" in raw_lower:
                result["intent"] = "research"
            elif "chat" in raw_lower or "chao" in raw_lower:
                result["intent"] = "chat"
            rprint(f"[yellow]Fallback intent: {result['intent']}[/yellow]")
    else:
        rprint("[red]❌ No JSON block found in LLM response[/red]")
    
    return result
