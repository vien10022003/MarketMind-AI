"""
Tool definitions for LLM providers.

Provides pre-built tool sets and helper functions for structured tool definitions.
Compatible with both LocalLlamaProvider (using transformers chat template)
and GeminiProvider (using google.genai types).
"""

from typing import List, Dict, Any


# ─────────────────────────────────────────────────────────────────────────
# TOOL DEFINITION STRUCTURES
# ─────────────────────────────────────────────────────────────────────────

def create_tool(
    name: str,
    description: str,
    properties: Dict[str, Any],
    required: List[str]
) -> Dict[str, Any]:
    """
    Create a tool definition compatible with both Llama and Gemini.
    
    Args:
        name: Tool name (e.g., "classify_intent")
        description: Human-readable description
        properties: JSON Schema properties dict
        required: List of required parameter names
    
    Returns:
        Dict compatible with apply_chat_template(tools=...) and google.genai.types
    """
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


# ─────────────────────────────────────────────────────────────────────────
# PRE-BUILT TOOL SETS
# ─────────────────────────────────────────────────────────────────────────

# Intent Classification - Used in router.py
INTENT_CLASSIFICATION_TOOLS = [
    create_tool(
        name="classify_intent",
        description="Classify user prompt into one of three intents: chat, knowledge, or research. IMPORTANT: If intent is 'chat', provide a helpful response. For other intents, you can leave response empty.",
        properties={
            "intent": {
                "type": "string",
                "enum": ["chat", "knowledge", "research"],
                "description": "The classified intent"
            },
            "response": {
                "type": "string",
                "description": "Provide a friendly, helpful response to the user"
            }
        },
        required=["intent", "response"]
    )
]

# Input Validation - Used in clarification.py
INPUT_VALIDATION_TOOLS = [
    create_tool(
        name="validate_input",
        description="Validate if user input contains all required information for market research",
        properties={
            "is_complete": {
                "type": "boolean",
                "description": "Whether input has all required information"
            },
            "missing_fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of missing field names"
            },
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Suggestions for improving the input"
            }
        },
        required=["is_complete", "missing_fields", "suggestions"]
    )
]

# Follow-up Questions - Used in clarification.py
CLARIFICATION_TOOLS = [
    create_tool(
        name="generate_questions",
        description="Generate follow-up questions and suggestions for clarification",
        properties={
            "questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of clarifying questions"
            },
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Suggestions to improve the research scope"
            }
        },
        required=["questions", "suggestions"]
    )
]

# Planning - Used in planning.py
PLANNING_TOOLS = [
    create_tool(
        name="create_research_plan",
        description="Create research questions and search steps for market analysis",
        properties={
            "research_questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key research questions"
            },
            "search_steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                    "required": ["query"]
                },
                "description": "Ordered list of search queries"
            }
        },
        required=["research_questions", "search_steps"]
    )
]

# ReAct Decision - Used in react.py
REACT_TOOLS = [
    create_tool(
        name="decide_action",
        description="Decide next action in ReAct loop: search for more information, refine query, or summarize findings",
        properties={
            "action": {
                "type": "string",
                "enum": ["search", "refine_query", "summarize"],
                "description": "Next action to take"
            },
            "query": {
                "type": "string",
                "description": "Search query if action is 'search', or refined query if 'refine_query'"
            },
            "reasoning": {
                "type": "string",
                "description": "Brief reasoning for the decision"
            }
        },
        required=["action", "query", "reasoning"]
    )
]

# Generate Search Queries - Used in knowledge_handler.py
GENERATE_SEARCH_QUERIES_TOOLS = [
    create_tool(
        name="generate_search_queries",
        description="Generate 3-4 search queries to comprehensively answer the user's question",
        properties={
            "search_queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of 3-4 optimized search queries"
            },
        },
        required=["search_queries"]
    )
]

# Synthesis - Used in synthesis.py
SYNTHESIS_TOOLS = [
    create_tool(
        name="synthesize_overview",
        description="Synthesize market research findings into structured market overview",
        properties={
            "tong_quan_thi_truong": {
                "type": "string",
                "description": "Market overview summary"
            },
            "tro_ly": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key data points and citations"
            }
        },
        required=["tong_quan_thi_truong", "tro_ly"]
    )
]

# Campaign Planning - Used in campaign.py
CAMPAIGN_TOOLS = [
    create_tool(
        name="create_campaign_plan",
        description="Create 7-day Discord campaign schedule with posting frequency and content types",
        properties={
            "duration_days": {
                "type": "integer",
                "description": "Campaign duration in days"
            },
            "posting_frequency": {
                "type": "string",
                "description": "Posting frequency (e.g., '2-3 times daily')"
            },
            "schedule": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of daily posting schedule items"
            }
        },
        required=["duration_days", "posting_frequency", "schedule"]
    )
]

# Strategy - Used in strategy.py
SWOT_TOOLS = [
    create_tool(
        name="generate_swot",
        description="Generate SWOT analysis from market research findings",
        properties={
            "strengths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of strengths"
            },
            "weaknesses": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of weaknesses"
            },
            "opportunities": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of opportunities"
            },
            "threats": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of threats"
            }
        },
        required=["strengths", "weaknesses", "opportunities", "threats"]
    )
]

# Content Expansion - Used in content_expander.py
CONTENT_EXPANSION_TOOLS = [
    create_tool(
        name="expand_content",
        description="Expand a content brief into a detailed Discord post with professional image prompt. Generate engaging caption with emojis and a detailed English image generation prompt.",
        properties={
            "expanded_caption": {
                "type": "string",
                "description": "Detailed, engaging Discord post caption with emojis and natural tone for product/advertising promotion"
            },
            "expanded_image_prompt": {
                "type": "string",
                "description": "Professional English image generation prompt with detailed keywords, style, lighting separated by commas"
            }
        },
        required=["expanded_caption", "expanded_image_prompt"]
    )
]

# System message for content expansion
SYSTEM_MESSAGE_CONTENT_EXPANDER = """You are an expert Discord content creator and professional image prompt writer.
Your role is to expand content briefs into:
1. Engaging Discord posts with natural tone, relevant emojis, and persuasive product promotion
2. Detailed English image generation prompts with specific keywords, style, and lighting

IMPORTANT: Always respond with valid JSON containing exactly: "expanded_caption" and "expanded_image_prompt"""


# ─────────────────────────────────────────────────────────────────────────
# SYSTEM MESSAGES
# ─────────────────────────────────────────────────────────────────────────

# Default system message for market research analyst
SYSTEM_MESSAGE_ANALYST = "You are a precise market research analyst. Provide structured, concise, and data-driven outputs."

# System message for intent classification
SYSTEM_MESSAGE_INTENT_CLASSIFIER = """You are an intent classification system. You must always respond with valid JSON and never add extra text.
Classify user prompts into exactly one of three categories:
1. "chat" - Casual greetings, simple conversation, thanking, asking about chatbot, common knowledge
2. "knowledge" - Questions requiring current information or high accuracy (e.g., GDP 2024, currency rates)
3. "research" - Marketing analysis, market research, competitive analysis, strategy questions
"""

# System message for input validation
SYSTEM_MESSAGE_INPUT_VALIDATOR = """You are an input validation system for market research. You must always respond with valid JSON.
Check if the input contains essential information: industry, target market, target segments, competitors (if known), time frame, and research goals."""

# System message for planning
SYSTEM_MESSAGE_PLANNER = """You are a market research planning expert. Create detailed research plans with specific search queries and focus areas."""

# System message for ReAct decision maker
SYSTEM_MESSAGE_REACT_DECIDER = """You are a ReAct decision engine. Based on current findings, decide whether to:
1. "search" - Search for more information
2. "refine_query" - Refine the search query
3. "summarize" - Synthesize findings into final answer

Always respond with valid JSON."""


# ─────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────

def build_messages_from_history(
    current_prompt: str,
    conversation_history: List[Dict[str, str]] = None,
    max_history: int = 2
) -> List[Dict[str, str]]:
    """
    Build messages list from current prompt and conversation history.
    
    Args:
        current_prompt: Current user message
        conversation_history: List of {"role": "user"|"assistant", "content": "..."} dicts
        max_history: Maximum number of previous messages to include (default 2)
    
    Returns:
        List of message dicts for apply_chat_template() or GenerateContentConfig
    
    Example:
        >>> msgs = build_messages_from_history(
        ...     current_prompt="Analyze the coffee market",
        ...     conversation_history=[
        ...         {"role": "user", "content": "What should I research?"},
        ...         {"role": "assistant", "content": "Start with market size..."}
        ...     ]
        ... )
        >>> len(msgs) == 3  # 2 history + 1 current
    """
    messages = []
    
    # Add conversation history (limit to max_history messages)
    if conversation_history:
        # Take only the last max_history messages
        history_to_use = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
        messages.extend(history_to_use)
    
    # Add current prompt as user message
    messages.append({
        "role": "user",
        "content": current_prompt
    })
    
    return messages


def convert_tools_to_gemini_format(tools: List[Dict[str, Any]]) -> List[Any]:
    """
    Convert tool definitions to google.genai.types format.
    
    Args:
        tools: List of tool dicts with {name, description, parameters}
    
    Returns:
        List of google.genai.types.FunctionDeclaration objects
    
    Note:
        Requires: from google import genai
        Used internally by GeminiProvider
    """
    try:
        from google.genai import types
    except ImportError:
        raise ImportError("google-genai package required. Install with: pip install google-genai")
    
    declarations = []
    for tool in tools:
        declaration = types.FunctionDeclaration(
            name=tool["name"],
            description=tool["description"],
            parameters=tool["parameters"]
        )
        declarations.append(declaration)
    
    return declarations
