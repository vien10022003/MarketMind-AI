"""
Local LLM Configuration & Initialization
Backwards compatibility layer - imports from llm_provider
"""

import os
from typing import Optional

# Import from new provider architecture
from .llm_provider import (
    LocalLLMConfig,
    LocalLlamaProvider,
    LLMProvider,
    get_llm_provider,
    initialize_llm as init_llm,
)


# Backwards compatibility function
def initialize_llm(provider_name: str = "llama") -> LLMProvider:
    """
    Initialize and return LLM provider instance
    
    Args:
        provider_name: "llama", "gemini-2.5", or "gemini-3.1"
    
    Returns:
        LLMProvider instance
    """
    return init_llm(provider_name)


if __name__ == "__main__":
    llm = initialize_llm("llama")
    test_prompt = "What is market research?"
    result = llm.generate(test_prompt, max_tokens=100)
    print(f"Test output: {result}")
