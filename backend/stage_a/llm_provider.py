"""
LLM Provider Architecture - Abstract factory pattern for multiple LLM backends
Supports: Local Llama, Gemini 2.5, Gemini 3.1

Instance Caching:
- LocalLlamaProvider instances are cached globally to avoid reloading the model
  into VRAM. The first instantiation loads the model, subsequent instantiations
  reuse the cached instance.
- Use clear_llama_cache() to explicitly unload the model if needed.
"""

import os
import gc
import time
import warnings
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import login
from rich import print as rprint

# Suppress warnings
warnings.filterwarnings('ignore', message='.*pad_token_id.*')
warnings.filterwarnings('ignore', message='.*max_new_tokens.*')
warnings.filterwarnings('ignore', message='.*LangChainTracer.*')
os.environ['LANGCHAIN_TRACING_V2'] = 'false'

# Global cache for LocalLlamaProvider instances
_local_llama_instance = None


# ─────────────────────────────────────────────────────────────────────────
# ABSTRACT BASE CLASS
# ─────────────────────────────────────────────────────────────────────────

class LLMProvider(ABC):
    """Abstract base class for LLM providers
    
    Supports both legacy (prompt-only) and new (structured) API:
    - New: generate(messages=[...], system_message="...", tools=[...])
    - Legacy: generate(prompt="...") - still supported for backward compatibility
    """
    
    @abstractmethod
    def generate(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_new_tokens: int = 1000
    ) -> str:
        """
        Generate text from messages or prompt.
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."} dicts
            prompt: Legacy single prompt string (if messages not provided)
            system_message: System instruction (prepended to messages if provided)
            tools: List of tool definitions {"name": "...", "description": "...", "parameters": {...}}
            temperature: Sampling temperature (0.0-1.0)
            max_new_tokens: Maximum tokens to generate
        
        Returns:
            Generated text string (caller responsible for JSON parsing)
        
        Note:
            If both messages and prompt provided, messages takes precedence.
            If system_message provided, it's prepended to the messages list.
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name for logging"""
        pass


# ─────────────────────────────────────────────────────────────────────────
# LOCAL LLAMA PROVIDER
# ─────────────────────────────────────────────────────────────────────────

@dataclass
class LocalLLMConfig:
    """Configuration for Local LLM"""
    model_name: str = os.getenv("STAGE_A_LOCAL_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
    temperature: float = float(os.getenv("STAGE_A_TEMPERATURE", "0.2"))
    max_new_tokens: int = int(os.getenv("STAGE_A_MAX_NEW_TOKENS", "1000"))
    device_map: str = os.getenv("STAGE_A_DEVICE_MAP", "auto")
    timeout_sec: int = int(os.getenv("STAGE_A_TIMEOUT_SEC", "120"))


class LocalLlamaProvider(LLMProvider):
    """Local LLM provider using Llama model"""
    
    def __init__(self, cfg: Optional[LocalLLMConfig] = None):
        global _local_llama_instance
        
        self.cfg = cfg or LocalLLMConfig()
        
        # Check if instance already exists with same model_name
        if _local_llama_instance is not None and _local_llama_instance.cfg.model_name == self.cfg.model_name:
            # Reuse existing instance - copy references
            self.tokenizer = _local_llama_instance.tokenizer
            self.model = _local_llama_instance.model
            self.pipe = _local_llama_instance.pipe
            rprint(f"[green]✅ Reusing cached Local LLM: {self.cfg.model_name}[/green]")
            return
        
        # HuggingFace login
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "hf..")
        if hf_token and hf_token != "hf..":
            login(token=hf_token)
        
        # Determine dtype based on CUDA availability
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        rprint(f"[yellow]Loading local model: {self.cfg.model_name}[/yellow]")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.cfg.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.cfg.model_name,
            device_map=self.cfg.device_map,
            torch_dtype=dtype,
        )
        
        # Create pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        
        # Cache this instance globally
        _local_llama_instance = self
        
        rprint(f"[green]✅ Local LLM loaded: {self.cfg.model_name}[/green]")
    
    @property
    def provider_name(self) -> str:
        return "local_llama"
    
    def generate(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_new_tokens: int = 1000
    ) -> str:
        """Generate text based on messages or prompt"""
        max_new_tokens = max_new_tokens or self.cfg.max_new_tokens
        temp = temperature if temperature is not None else self.cfg.temperature

        # Build messages list
        if messages is None:
            if prompt is None:
                raise ValueError("Either 'messages' or 'prompt' must be provided")
            # Legacy: build messages from prompt
            final_messages = [
                {"role": "user", "content": prompt}
            ]
        else:
            final_messages = list(messages)  # Copy to avoid mutation
        
        # Prepend system message if provided
        if system_message:
            final_messages.insert(0, {"role": "system", "content": system_message})
        elif not any(m.get("role") == "system" for m in final_messages):
            # Add default system message if none exists
            final_messages.insert(0, {
                "role": "system",
                "content": "You are a precise market research analyst. Return concise and structured outputs."
            })

        # Apply chat template
        if hasattr(self.tokenizer, "apply_chat_template"):
            model_input = self.tokenizer.apply_chat_template(
                final_messages,
                tools=tools,  # Pass tools if available
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            # Fallback: use last user message as prompt
            user_msgs = [m.get("content", "") for m in final_messages if m.get("role") == "user"]
            model_input = user_msgs[-1] if user_msgs else prompt or ""

        # Generate output
        output = self.pipe(
            model_input,
            max_new_tokens=max_new_tokens,
            do_sample=temp > 0,
            temperature=temp,
            top_p=0.9,
            repetition_penalty=1.15,
            return_full_text=True,
        )[0]["generated_text"]

        # Remove input from output
        if output.startswith(model_input):
            output = output[len(model_input):]
        
        # Cleanup GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
        return output.strip()


# ─────────────────────────────────────────────────────────────────────────
# GEMINI PROVIDER
# ─────────────────────────────────────────────────────────────────────────

class GeminiProvider(LLMProvider):
    """Gemini API provider"""
    
    def __init__(self, model_variant: str = "gemini-2.5-flash-lite"):
        """
        Initialize Gemini provider
        
        Args:
            model_variant: Either "gemini-2.5-flash-lite" or "gemini-3.1-flash-lite-preview"
        """
        self.model_variant = model_variant
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            rprint("[red]❌ GEMINI_API_KEY not found in environment[/red]")
            raise ValueError("GEMINI_API_KEY environment variable is required for Gemini provider")
        
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            rprint(f"[green]✅ Gemini client initialized: {model_variant}[/green]")
        except ImportError:
            rprint("[red]❌ google-genai package not installed. Install it with: pip install google-genai[/red]")
            raise
        except Exception as e:
            rprint(f"[red]❌ Failed to initialize Gemini client: {e}[/red]")
            raise
    
    @property
    def provider_name(self) -> str:
        return f"gemini_{self.model_variant.replace('.', '_').replace('-', '_')}"
    
    def generate(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        prompt: Optional[str] = None,
        system_message: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.2,
        max_new_tokens: int = 1000
    ) -> str:
        """Generate text using Gemini API with structured tools support"""
        # Build messages list
        if messages is None:
            if prompt is None:
                raise ValueError("Either 'messages' or 'prompt' must be provided")
            # Legacy: build messages from prompt
            final_messages = [
                {"role": "user", "content": prompt}
            ]
        else:
            final_messages = list(messages)  # Copy to avoid mutation
        
        # Prepend system message if provided
        if system_message:
            final_messages.insert(0, {"role": "system", "content": system_message})
        elif not any(m.get("role") == "system" for m in final_messages):
            # Add default system message if none exists
            final_messages.insert(0, {
                "role": "system",
                "content": "You are a precise market research analyst. Return concise and structured outputs."
            })
        
        # Build GenerateContentConfig
        try:
            from google.genai import types
            from .tool_definitions import convert_tools_to_gemini_format
        except ImportError:
            raise ImportError("google-genai package required. Install with: pip install google-genai")
        
        # Convert messages to Gemini format
        # Gemini API expects different format than OpenAI
        gemini_contents = []
        gemini_system = None
        
        for msg in final_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                # Store system message separately
                gemini_system = content
            elif role == "user":
                gemini_contents.append(types.Content(role="user", parts=[types.Part(text=content)]))
            elif role == "assistant":
                gemini_contents.append(types.Content(role="model", parts=[types.Part(text=content)]))
        
        # If no user/assistant messages, just send the last content as user message
        if not gemini_contents and final_messages:
            last_msg = final_messages[-1]
            gemini_contents.append(types.Content(role="user", parts=[types.Part(text=last_msg.get("content", ""))]))
        
        # Build GenerateContentConfig with system instruction
        config_dict = {
            "temperature": temperature,
            "max_output_tokens": max_new_tokens,
        }
        
        # Add system instruction to config if available
        if gemini_system:
            config_dict["system_instruction"] = gemini_system
        
        # Convert tools to Gemini format if provided
        if tools:
            tool_declarations = convert_tools_to_gemini_format(tools)
            config_dict["tools"] = [types.Tool(function_declarations=tool_declarations)]
        
        config = types.GenerateContentConfig(**config_dict)
        
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Build request parameters
                request_kwargs = {
                    "model": self.model_variant,
                    "contents": gemini_contents,
                    "config": config
                }
                
                response = self.client.models.generate_content(**request_kwargs)
                
                if response:
                    # Try to get text response first
                    if response.text:
                        return response.text.strip()
                    
                    # Handle function call responses
                    if hasattr(response, 'candidates') and response.candidates:
                        for candidate in response.candidates:
                            if hasattr(candidate, 'content') and candidate.content:
                                # Check for function calls
                                for part in candidate.content.parts:
                                    if hasattr(part, 'function_call') and part.function_call:
                                        # Extract function call args and convert to JSON
                                        func_call = part.function_call
                                        # Build JSON response with function name and parameters
                                        result = {
                                            "name": func_call.name,
                                            "parameters": func_call.args
                                        }
                                        return json.dumps(result)
                                
                                # Try to extract text from text parts
                                text_parts = []
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        text_parts.append(part.text)
                                
                                if text_parts:
                                    return ' '.join(text_parts).strip()
                    
                    rprint(f"[yellow]⚠️  Gemini returned no text or function call content[/yellow]")
                    return ""
                else:
                    rprint(f"[yellow]⚠️  Gemini returned empty response[/yellow]")
                    return ""
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Rate limiting - exponential backoff
                if "rate" in error_msg or "quota" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                        rprint(f"[yellow]⚠️  Rate limited. Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})[/yellow]")
                        time.sleep(wait_time)
                        continue
                
                # API key error
                if "api_key" in error_msg or "authentication" in error_msg or "unauthorized" in error_msg:
                    rprint(f"[red]❌ Gemini API authentication failed: {e}[/red]")
                    raise
                
                # Last attempt failed
                if attempt == max_retries - 1:
                    rprint(f"[red]❌ Gemini API error (final attempt): {e}[/red]")
                    raise
                
                # Other errors - retry
                rprint(f"[yellow]⚠️  Gemini API error, retrying... (attempt {attempt + 1}/{max_retries}): {e}[/yellow]")
                time.sleep(2 ** attempt)


# ─────────────────────────────────────────────────────────────────────────
# FACTORY FUNCTION
# ─────────────────────────────────────────────────────────────────────────

def get_llm_provider(provider_name: str = "llama") -> LLMProvider:
    """
    Factory function to get LLM provider instance
    
    Args:
        provider_name: One of "llama", "gemini-2.5", "gemini-3.1"
    
    Returns:
        LLMProvider instance
    
    Raises:
        ValueError: If provider_name is invalid or required env vars are missing
    
    Note:
        For LocalLlamaProvider, instances are cached globally to avoid reloading
        the model into VRAM. The first call to get_llm_provider("llama") will 
        load the model, subsequent calls will reuse the cached instance.
    """
    provider_name = provider_name.lower().strip()
    
    if provider_name == "llama":
        return LocalLlamaProvider()
    
    elif provider_name == "gemini-2.5":
        return GeminiProvider(model_variant="gemini-2.5-flash-lite")
    
    elif provider_name == "gemini-3.1":
        return GeminiProvider(model_variant="gemini-3.1-flash-lite-preview")
    
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Supported providers: 'llama', 'gemini-2.5', 'gemini-3.1'"
        )


def clear_llama_cache():
    """Clear the cached LocalLlamaProvider instance (useful for memory cleanup)"""
    global _local_llama_instance
    _local_llama_instance = None
    rprint("[yellow]⚠️  Cleared cached Local LLM instance[/yellow]")



# ─────────────────────────────────────────────────────────────────────────
# INITIALIZATION FUNCTION
# ─────────────────────────────────────────────────────────────────────────

def initialize_llm(provider_name: str = "llama") -> LLMProvider:
    """
    Initialize and return LLM provider instance
    
    Args:
        provider_name: One of "llama", "gemini-2.5", "gemini-3.1"
    
    Returns:
        LLMProvider instance
    """
    return get_llm_provider(provider_name)


if __name__ == "__main__":
    # Test script
    llm = initialize_llm("llama")
    test_prompt = "What is market research?"
    result = llm.generate(test_prompt, max_tokens=100)
    print(f"Test output: {result}")
