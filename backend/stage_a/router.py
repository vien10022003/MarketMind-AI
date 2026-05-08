import json
from typing import Dict, Any, Optional, List
from rich import print as rprint

from .llm_provider import LLMProvider
from .tool_definitions import (
    INTENT_CLASSIFICATION_TOOLS,
    SYSTEM_MESSAGE_INTENT_CLASSIFIER,
    build_messages_from_history
)
from .clarification import extract_first_json_block, normalize_tool_response

def classify_intent_and_respond(
    llm: LLMProvider,
    user_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Classifies the user's prompt into one of three intents:
      - "chat": casual greeting or simple conversation
      - "knowledge": hard/complex question that may need web search for accurate answer
      - "research": marketing research / market analysis request
    
    If intent is "chat", generates a friendly response.
    
    Args:
        llm: The LLM provider instance (LocalLlamaProvider or GeminiProvider)
        user_prompt: The current user prompt
        conversation_history: List of recent conversation turns [{"role": "user"|"assistant", "content": "..."}]
    
    Returns:
        Dict with keys: intent, response, reasoning
    """
    # Build messages list from conversation history (max 2 previous messages + current prompt)
    messages = build_messages_from_history(user_prompt, conversation_history, max_history=2)
    
    # Debug output
    rprint(f"[blue]--- Intent Classification ---[/blue]")
    rprint(f"[dim]Messages being sent to LLM:[/dim]")
    for msg in messages:
        rprint(f"  {msg['role']}: {msg['content'][:100]}...")
    
    # Call generate with structured parameters
    raw = llm.generate(
        messages=messages,
        system_message=SYSTEM_MESSAGE_INTENT_CLASSIFIER,
        tools=INTENT_CLASSIFICATION_TOOLS,
        max_new_tokens=500
    )
    
    block = extract_first_json_block(raw)
    
    rprint(f"[cyan]--- Intent Classification Response ---[/cyan]")
    rprint(raw)
    
    result = {
        "intent": "research",
        "response": "",
        "reasoning": ""
    }
    
    if block:
        try:
            parsed = json.loads(block)
            # Normalize tool calling response format
            parsed = normalize_tool_response(parsed)
            
            # Validate intent value
            valid_intents = {"chat", "knowledge", "research"}
            if parsed.get("intent") not in valid_intents:
                rprint(f"[yellow]⚠️ Invalid intent '{parsed.get('intent')}', defaulting to research[/yellow]")
                parsed["intent"] = "research"
            
            result.update(parsed)
            rprint(f"[green]✅ Intent Classification: {result.get('intent')}[/green]")
            
            # Fallback: If intent is chat but response is empty, generate one
            if result.get("intent") == "chat" and not result.get("response", "").strip():
                rprint(f"[yellow]⚠️  Chat intent detected but response is empty, generating fallback response[/yellow]")
                fallback_response = llm.generate(
                    messages=[{"role": "user", "content": user_prompt}],
                    system_message="You are a friendly AI assistant. Respond naturally and helpfully to the user's message.",
                    max_new_tokens=300
                )
                result["response"] = fallback_response.strip() if fallback_response else "Xin lỗi, tôi không thể trả lời lúc này. Vui lòng thử lại."
                rprint(f"[green]✅ Generated fallback response[/green]")
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
