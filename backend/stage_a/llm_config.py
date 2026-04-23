"""
Local LLM Configuration & Initialization
Handles Llama model setup and text generation
"""

import os
from dataclasses import dataclass
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from huggingface_hub import login
from rich import print as rprint


@dataclass
class LocalLLMConfig:
    """Configuration for Local LLM"""
    model_name: str = os.getenv("STAGE_A_LOCAL_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
    temperature: float = float(os.getenv("STAGE_A_TEMPERATURE", "0.2"))
    max_new_tokens: int = int(os.getenv("STAGE_A_MAX_NEW_TOKENS", "700"))
    device_map: str = os.getenv("STAGE_A_DEVICE_MAP", "auto")
    timeout_sec: int = int(os.getenv("STAGE_A_TIMEOUT_SEC", "120"))


class LocalTextGenerator:
    """Local LLM text generation wrapper"""
    
    def __init__(self, cfg: LocalLLMConfig):
        self.cfg = cfg
        
        # HuggingFace login
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", "hf..")
        if hf_token and hf_token != "hf..":
            login(token=hf_token)
        
        # Determine dtype based on CUDA availability
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        rprint(f"[yellow]Loading local model: {cfg.model_name}[/yellow]")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            cfg.model_name,
            device_map=cfg.device_map,
            torch_dtype=dtype,
        )
        
        # Create pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )
        
        rprint(f"[green]✅ Local LLM loaded: {cfg.model_name}[/green]")

    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate text based on prompt"""
        max_tokens = max_new_tokens or self.cfg.max_new_tokens
        temp = self.cfg.temperature if temperature is None else temperature

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
            max_new_tokens=max_tokens,
            do_sample=temp > 0,
            temperature=temp,
            top_p=0.9,
            return_full_text=True,
        )[0]["generated_text"]

        # Remove input from output
        if output.startswith(model_input):
            output = output[len(model_input):]
        
        return output.strip()


def initialize_llm() -> LocalTextGenerator:
    """Initialize and return LocalTextGenerator instance"""
    cfg = LocalLLMConfig()
    llm = LocalTextGenerator(cfg)
    return llm


if __name__ == "__main__":
    llm = initialize_llm()
    test_prompt = "What is market research?"
    result = llm.generate(test_prompt, max_new_tokens=100)
    print(f"Test output: {result}")
