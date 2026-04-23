# Stage A Market Research Agent - Usage Guide

Complete guide for using the modularized Stage A pipeline.

## 🎯 Use Cases

### 1. Market Research Report Generation

Generate comprehensive market research reports programmatically:

```python
from stage_a.main import run_pipeline

output = run_pipeline(
    user_prompt="Analyze the electric vehicle market in Vietnam",
    industry="Automotive",
    market="Vietnam",
    timeframe="Last 12 months"
)

# Results
print(output.tong_quan_thi_truong)      # Market overview
print(output.phan_tich_doi_thu)         # Competitor analysis
print(output.xu_huong_nganh)            # Industry trends
print(output.phan_khuc_va_insight_khach_hang)  # Customer insights
```

### 2. Web API Server

Run as a REST API for multiple client requests:

```bash
# Start server
python stage_a/main.py server --port 5000 --no-ngrok

# Or with ngrok for public access
python stage_a/main.py server --port 5000
```

### 3. Pipeline Customization

Modify specific pipeline steps:

```python
from stage_a.02_environment import load_environment
from stage_a.03_llm_config import initialize_llm
from stage_a.04_data_models import StageAInput
from stage_a.05_clarification import clarify_user_prompt
from stage_a.06_planning import planner_chain
from stage_a.08_react import run_react_loop
from stage_a.09_evidence_processing import normalize_and_filter_evidence
from stage_a.10_synthesis import synthesize_stage_a_report

# Initialize
config = load_environment()
llm = initialize_llm()

# Step 1: Clarification
initial_input = StageAInput(user_prompt="Your research question")
clarification = clarify_user_prompt(llm, "Research question", initial_input)
research_input = clarification["clarified_input"]

# Step 2: Planning with custom settings
plan = planner_chain(llm, research_input, max_steps=10)

# Step 3: ReAct loop with custom tool calls
react_result = run_react_loop(llm, plan, max_tool_calls=20)

# Step 4: Custom evidence filtering
evidence_df = normalize_and_filter_evidence(react_result["evidence"])

# Step 5: Report synthesis
report = synthesize_stage_a_report(llm, research_input, evidence_df)
```

## 📡 REST API Endpoints

### Main Research Endpoint

**POST** `/api/research/stage_a`

Request:
```json
{
  "user_prompt": "Tìm hiểu thị trường xe điện tại Việt Nam",
  "nganh_hang": "Xe điện",
  "thi_truong_muc_tieu": "Việt Nam",
  "phan_khuc_quan_tam": ["Khách hàng trẻ", "Khách hàng cao cấp"],
  "doi_thu_seed": ["Tesla", "BYD"],
  "khung_thoi_gian": "12 thang gan nhat",
  "muc_tieu_nghien_cuu": ["Market size", "Trends"]
}
```

Response (Streaming NDJSON):
```
{"status": "starting", "message": "Khởi tạo tác vụ Giai đoạn A..."}
{"status": "progress", "message": "LLM đang phân tích yêu cầu..."}
{"status": "clarification_provided", "detected_info": {...}, "questions": [...]}
{"status": "plan_completed", "plan": {...}}
{"status": "react_completed", "react_summary": {...}}
{"status": "evidence_ready", "evidence": [...], "evidence_count": {...}}
{"status": "report_ready", "report": {...}}
{"status": "completed", "mongodb_id": "...", "timestamp": "..."}
```

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "llm_ready": true,
  "mongodb_ready": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔧 Configuration Examples

### Minimal Setup

```python
from stage_a.04_data_models import StageAInput
input_data = StageAInput(user_prompt="Market research topic")
# Uses defaults for all other fields
```

### Advanced Setup

```python
input_data = StageAInput(
    user_prompt="Comprehensive market analysis",
    nganh_hang="Technology",
    thi_truong_muc_tieu="Asia",
    phan_khuc_quan_tam=["SMEs", "Enterprises", "Startups"],
    doi_thu_seed=["Company A", "Company B", "Company C"],
    khung_thoi_gian="Last 24 months",
    muc_tieu_nghien_cuu=["Market size", "Growth rate", "Key players"]
)
```

### LLM Tuning

```bash
# .env configuration for creative vs deterministic
STAGE_A_TEMPERATURE=0.7         # Creative (more random)
STAGE_A_MAX_NEW_TOKENS=1000    # Longer responses

STAGE_A_TEMPERATURE=0.1         # Deterministic
STAGE_A_MAX_NEW_TOKENS=500     # Concise responses
```

## 📊 Output Examples

### Markdown Report

```markdown
# Báo Cáo Giai Đoạn A - Xe điện (Việt Nam)

**Thời gian**: 12 thang gan nhat

## 1. Tổng Quan Thị Trường

Thị trường xe điện Việt Nam đang tăng trưởng với tốc độ 45% hàng năm...

[Detailed analysis with citations]

## 2. Phân Tích Đối Thủ

Tesla là người dẫn đầu thị trường với...

[Competitor analysis]

## 3. Xu Hướng Ngành

- Chuyển đổi sang electric powertrain
- Tích hợp AI cho autonomous driving
- Tiêu chuẩn pin mới

## 4. Phân Khúc & Insight Khách Hàng

Khách hàng trẻ (18-35) ưu tiên:
- Giá cả hợp lý
- Charging infrastructure...

## Tài Liệu Tham Khảo

1. Tesla Market Share Report - [url]
2. Vietnam EV Market Analysis - [url]
```

### JSON Response

```json
{
  "input": {
    "user_prompt": "...",
    "nganh_hang": "xe_dien",
    "thi_truong_muc_tieu": "Vietnam"
  },
  "report": {
    "tong_quan_thi_truong": "...",
    "phan_tich_doi_thu": "...",
    "xu_huong_nganh": "...",
    "phan_khuc_va_insight_khach_hang": "...",
    "citations": [
      {
        "title": "...",
        "url": "...",
        "source_score": 0.9
      }
    ]
  },
  "metadata": {
    "tool_calls": 14,
    "total_evidence": 120,
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

## 🔄 Workflow Examples

### Batch Processing

```python
queries = [
    "Market analysis for AI startups",
    "EV market trends in Southeast Asia",
    "Fintech landscape in Vietnam"
]

results = []
for query in queries:
    output = run_pipeline(query)
    results.append(output)
    print(f"✅ Processed: {query}")
```

### With Custom Post-Processing

```python
from stage_a.main import run_pipeline
from stage_a.11_output_formatting import build_markdown_report
import json

output = run_pipeline("Your research prompt")

# Save Markdown
markdown = build_markdown_report(research_input, output)
with open("report.md", "w") as f:
    f.write(markdown)

# Save JSON
with open("report.json", "w") as f:
    json.dump(output.model_dump(), f, ensure_ascii=False, indent=2)

# Custom processing
print(f"Generated {len(output.citations)} citations")
print(f"Report sections: 4 major sections")
```

## 🐛 Troubleshooting

### LLM Issues

**Problem**: Model not found

```bash
# Download the model first
python -c "from transformers import AutoModelForCausalLM; \
AutoModelForCausalLM.from_pretrained('meta-llama/Llama-3.2-3B-Instruct')"
```

**Problem**: Out of memory (OOM)

```bash
# Reduce token length
STAGE_A_MAX_NEW_TOKENS=400
```

### Tavily Search Issues

**Problem**: API key invalid

```bash
# Verify .env
echo $TAVILY_API_KEY
```

## 📈 Performance Tuning

### Speed vs Quality Trade-offs

```python
# Fast (default)
planner_chain(llm, input_data, max_steps=8)
run_react_loop(llm, plan, max_tool_calls=14)

# Thorough
planner_chain(llm, input_data, max_steps=15)
run_react_loop(llm, plan, max_tool_calls=30)
```

### Resource Optimization

```python
# Reduce evidence processing
from stage_a.09_evidence_processing import get_top_evidence
top_evidence = get_top_evidence(evidence_df, top_n=10)

# Batch processing with pooling
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    jobs = [executor.submit(run_pipeline, q) for q in queries]
```

## 🔐 Security Considerations

1. **API Keys**: Keep `.env` in `.gitignore`
2. **Database**: Use connection pooling for MongoDB
3. **Ngrok**: Regenerate tokens regularly
4. **Rate Limiting**: Implement in Flask for production

## 📚 API Documentation

See [README.md](README.md) for:
- Module breakdown
- Directory structure
- Environment setup
- Quick start guide

## 💡 Best Practices

1. **Error Handling**: Always wrap calls in try-except
2. **Logging**: Use rich output for monitoring
3. **Validation**: Check input before submission
4. **Storage**: Archive reports to MongoDB
5. **Monitoring**: Check `/health` endpoint regularly

## 🤝 Contributing

To extend the pipeline:

1. Create new module `NN_feature.py`
2. Add to `__init__.py`
3. Integrate with main.py
4. Update documentation

## 📞 Support

- Check logs for error details
- Review `.env` configuration
- Test individual modules first
- Consult API documentation

---

**Last Updated**: 2024
**Version**: 1.0.0
