from google import genai
from google.genai import types
from google.colab import userdata

client = genai.Client(
    api_key=userdata.get("GEMINI_API_KEY")
)

weather_fn = types.FunctionDeclaration(
    name="get_weather",
    description="Get weather",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        },
        "required": ["city"]
    }
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Thời tiết Hà Nội hôm nay?",
    config=types.GenerateContentConfig(
        system_instruction="""
        You must always use tools when available.
        Never answer directly if a tool can satisfy the request.
        """,# ép buộc mô hình trong role system nếu bắt buộc json, các thông tin cần cung cấp như ngành hàng cũng có thể cung cấp ở role system
        tools=[
            types.Tool(
                function_declarations=[weather_fn]
            )
        ]
    )
)

call = response.function_calls[0]

tool_result = {
    "temperature": "29°C",
    "condition": "Cloudy"
}

final = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        "Thời tiết Hà Nội hôm nay?",
        types.Part.from_function_response(
            name=call.name,
            response=tool_result
        )
    ]
)

print(final.text)