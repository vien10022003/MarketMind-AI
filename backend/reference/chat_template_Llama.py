import torch
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "your-huggingface-model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16
)

print("Loaded.")

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name"
                }
            },
            "required": ["city"]
        }
    }
]

def get_weather(city):
    return {
        "city": city,
        "temperature": "29°C",
        "condition": "Cloudy"
    }

def generate(messages, tools=None, max_new_tokens=256):
    prompt = tokenizer.apply_chat_template(
        messages,
        tools=tools,
        add_generation_prompt=True,
        tokenize=False
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    ).to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False
    )

    response = tokenizer.decode(
        outputs[0][inputs.input_ids.shape[-1]:],
        skip_special_tokens=True
    )

    return response

messages = [
    {
        "role": "system",
        "content": """You must always respond with a function call JSON.
        Never answer with natural language.
        You must choose exactly one tool from the provided tools.
        """ # ép buộc mô hình trong role system nếu bắt buộc json, các thông tin cần cung cấp như ngành hàng cũng có thể cung cấp ở role system
    },
    {
        "role": "user",
        "content": "Thời tiết Hà Nội hôm nay thế nào?"
    }
]

response = generate(messages, tools)

print("MODEL TOOL CALL:")
print(response)