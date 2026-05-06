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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
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
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_new_tokens: int = 1000
    ) -> str:
        """Generate text from prompt"""
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
        prompt: str,
        temperature: float = 0.2,
        max_new_tokens: int = 1000
    ) -> str:
        """Generate text based on prompt"""
        max_new_tokens = max_new_tokens or self.cfg.max_new_tokens
        temp = temperature if temperature is not None else self.cfg.temperature

        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are a precise market research analyst. Return concise and structured outputs."
            },
            {"role": "user", "content": prompt},
        ]

        # Apply chat template if available
        if hasattr(self.tokenizer, "apply_chat_template"):
            model_input = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            model_input = prompt

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
        prompt: str,
        temperature: float = 0.2,
        max_new_tokens: int = 1000
    ) -> str:
        """Generate text using Gemini API with retry logic"""
        messages = [
            {
                "role": "user",
                "content": f"You are a precise market research analyst. Return concise and structured outputs.\n\n{prompt}"
            }
        ]
        
        # Retry logic with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_variant,
                    contents=messages,
                    config={
                        "temperature": temperature,
                        "max_output_tokens": max_new_tokens,
                    }
                )
                
                if response and response.text:
                    return response.text.strip()
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
# BACKWARDS COMPATIBILITY - LocalTextGenerator wrapper
# ─────────────────────────────────────────────────────────────────────────

class LocalTextGenerator(LocalLlamaProvider):
    """Backwards compatibility wrapper - same as LocalLlamaProvider"""
    pass


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
