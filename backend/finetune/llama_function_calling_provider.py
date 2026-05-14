"""
Llama Function Calling Fine-tuned Model Provider
Integration module for using fine-tuned model in MarketMind-AI
"""

import json
import torch
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class LlamaFunctionCallingProvider:
    """
    Provider for fine-tuned Llama model with function calling capability
    Replaces or augments the existing LLM provider with function calling optimized model
    """
    
    def __init__(self, model_path: str = "./llama_function_calling_finetune"):
        """
        Initialize the fine-tuned model provider
        
        Args:
            model_path: Path to fine-tuned model directory
        """
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self._load_model()
    
    
    def _load_model(self):
        """Load the fine-tuned model and tokenizer"""
        try:
            from unsloth import FastLanguageModel
            from peft import PeftModel
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            print(f"📦 Loading fine-tuned model from {self.model_path}...")
            
            # Check if it's a LoRA adapter or full model
            if Path(self.model_path).exists():
                # Try to load as full model first
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        device_map=self.device,
                        torch_dtype=torch.bfloat16,
                        load_in_4bit=True
                    )
                    print(f"✅ Loaded as full model")
                except:
                    # Try loading base model + LoRA adapter
                    base_model_name = "meta-llama/Llama-2-7b-chat-hf"
                    base_model, self.tokenizer = FastLanguageModel.from_pretrained(
                        model_name=base_model_name,
                        dtype=torch.bfloat16,
                        max_seq_length=2048,
                        load_in_4bit=True,
                    )
                    self.model = PeftModel.from_pretrained(base_model, self.model_path)
                    print(f"✅ Loaded base model + LoRA adapter")
            
            # Prepare for inference
            self.model.eval()
            print(f"✅ Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    
    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON function call from model response
        
        Args:
            response: Model generated text
        
        Returns:
            Parsed JSON dict or None if not found
        """
        try:
            # Find JSON block
            json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        return None
    
    
    def validate_function_call(self, response: str) -> bool:
        """
        Validate if response contains valid function call
        
        Returns:
            True if valid JSON with name and parameters
        """
        try:
            data = self.extract_json_from_response(response)
            return data is not None and "name" in data and "parameters" in data
        except:
            return False
    
    
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_message: str = "",
        tools: Optional[List[Dict[str, Any]]] = None,
        max_new_tokens: int = 500,
        temperature: float = 0.3,
        top_p: float = 0.95,
    ) -> str:
        """
        Generate response with function calling support
        
        Args:
            messages: List of message dicts with role and content
            system_message: System message for the model
            tools: List of tool definitions (optional)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more focused)
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated response text
        """
        try:
            # Build messages with system prompt
            full_messages = []
            
            if system_message:
                full_messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            # Add tools to first user message if provided
            if tools:
                first_user_idx = None
                for i, msg in enumerate(messages):
                    if msg["role"] == "user":
                        first_user_idx = i
                        break
                
                if first_user_idx is not None:
                    # Inject tool definitions into first user message
                    tool_instructions = "Given the following functions, please respond with a JSON for a function call with its proper arguments that best answers the given prompt.\n\n"
                    tool_instructions += 'Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}. Do not use variables.\n\n'
                    
                    for tool in tools:
                        tool_instructions += json.dumps(tool, indent=4) + "\n\n"
                    
                    # Combine with original message
                    first_user_msg = messages[first_user_idx].copy()
                    first_user_msg["content"] = tool_instructions + first_user_msg["content"]
                    
                    full_messages.extend(messages[:first_user_idx])
                    full_messages.append(first_user_msg)
                    full_messages.extend(messages[first_user_idx + 1:])
                else:
                    full_messages.extend(messages)
            else:
                full_messages.extend(messages)
            
            # Apply chat template
            text = self.tokenizer.apply_chat_template(
                full_messages,
                tokenize=False,
                add_generation_prompt=True
            )
            
            # Tokenize
            model_inputs = self.tokenizer([text], return_tensors="pt")
            
            if torch.cuda.is_available():
                model_inputs = model_inputs.to(self.device)
            
            # Generate
            with torch.no_grad():
                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            
            # Decode
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            return response.strip()
        
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            raise
    
    
    def generate_with_function_call(
        self,
        messages: List[Dict[str, str]],
        system_message: str = "",
        tools: Optional[List[Dict[str, Any]]] = None,
        max_new_tokens: int = 500,
    ) -> Dict[str, Any]:
        """
        Generate response and extract function call
        
        Returns:
            Dict with keys:
                - success: bool, whether valid function call was extracted
                - response: str, full model response
                - function_call: dict, parsed JSON if success
                - error: str, error message if failed
        """
        try:
            response = self.generate(
                messages=messages,
                system_message=system_message,
                tools=tools,
                max_new_tokens=max_new_tokens,
            )
            
            function_call = self.extract_json_from_response(response)
            is_valid = self.validate_function_call(response)
            
            return {
                "success": is_valid,
                "response": response,
                "function_call": function_call,
            }
        
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "function_call": None,
                "error": str(e)
            }
    
    
    def batch_generate(
        self,
        batch_messages: List[List[Dict[str, str]]],
        system_message: str = "",
        tools: Optional[List[Dict[str, Any]]] = None,
        max_new_tokens: int = 500,
    ) -> List[str]:
        """
        Generate responses for a batch of message lists
        
        Args:
            batch_messages: List of message lists
            system_message: System message (same for all)
            tools: Tool definitions (same for all)
            max_new_tokens: Max tokens per response
        
        Returns:
            List of responses
        """
        responses = []
        for messages in batch_messages:
            response = self.generate(
                messages=messages,
                system_message=system_message,
                tools=tools,
                max_new_tokens=max_new_tokens,
            )
            responses.append(response)
        return responses


def load_finetuned_model(model_path: str = "./llama_function_calling_finetune"):
    """
    Convenience function to load fine-tuned model
    
    Args:
        model_path: Path to fine-tuned model
    
    Returns:
        LlamaFunctionCallingProvider instance
    """
    return LlamaFunctionCallingProvider(model_path)


# Example usage
if __name__ == "__main__":
    # Load model
    provider = load_finetuned_model()
    
    # Define a tool
    tools = [
        {
            "name": "classify_intent",
            "description": "Classify user intent",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string",
                        "enum": ["chat", "knowledge", "research"]
                    },
                    "response": {"type": "string"},
                    "reasoning": {"type": "string"}
                },
                "required": ["intent", "response", "reasoning"]
            }
        }
    ]
    
    # Generate with function calling
    messages = [
        {
            "role": "user",
            "content": "Phân tích thị trường cà phê specialty Việt Nam"
        }
    ]
    
    result = provider.generate_with_function_call(
        messages=messages,
        system_message="You are a market research analyst",
        tools=tools,
    )
    
    print(f"Success: {result['success']}")
    print(f"Function call: {result['function_call']}")
