import json
from typing import Dict, Any
from rich import print as rprint

from .llm_config import LocalTextGenerator
from .clarification import extract_first_json_block

def classify_intent_and_respond(llm: LocalTextGenerator, user_prompt: str) -> Dict[str, Any]:
    """
    Classifies the user's prompt as either a general chat message or a marketing research request.
    If it's a general chat message, it generates a response.
    
    Returns:
    - intent: "chat" or "research"
    - response: generated chat response (if intent is "chat")
    """
    prompt = f"""
Ban la mot he thong phan loai y dinh nguoi dung.
Nhiem vu: Xac dinh xem cau hoi cua nguoi dung la mot cau hoi/chao hoi thong thuong hay la mot yeu cau nguyen cuu thi truong/marketing.
Neu la cau chao hoi hoac hoi dap thong thuong, ban phai dua ra cau tra loi than thien nhu mot chatbot.
Neu la yeu cau nguyen cuu thi truong (vi du: yeu cau tim hieu ve nganh hang, thi truong muc tieu, doi thu canh tranh, v.v.), chi can phan loai do la "research".

User prompt: "{user_prompt}"

YEU CAU (Chi tra ve JSON, khong van ban):
{{
  "intent": "chat" | "research",
  "response": "Cau tra loi neu intent la 'chat', nguoc lai de trong ''"
}}
"""
    raw = llm.generate(prompt, max_new_tokens=400)
    block = extract_first_json_block(raw)
    
    result = {
        "intent": "research",
        "response": ""
    }
    
    if block:
        try:
            parsed = json.loads(block)
            result.update(parsed)
            rprint(f"[green]✅ Intent Classification completed: {result.get('intent')}[/green]")
        except json.JSONDecodeError:
            rprint("[yellow]⚠️ Intent Classification JSON parse failed, defaulting to research[/yellow]")
    
    return result
