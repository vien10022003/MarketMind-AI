# Stage A Market Research Agent - Python Package

Modular reorganization of the Jupyter notebook `A_stage_local_marketing_agen-v2.ipynb` into production-ready Python modules.

## 📁 Directory Structure

```
stage_a/
├── __init__.py                      # Package initialization
├── 02_environment.py                # Environment & directory setup
├── 03_llm_config.py                 # Local LLM configuration
├── 04_data_models.py                # Pydantic models
├── 05_clarification.py              # 2-step input clarification
├── 06_planning.py                   # Research planning chain
├── 07_tavily_search.py              # Web search integration
├── 08_react.py                      # ReAct reasoning loop
├── 09_evidence_processing.py        # Evidence normalization & filtering
├── 10_synthesis.py                  # Report generation
├── 11_output_formatting.py          # Output format conversion
├── 12_mongodb.py                    # MongoDB storage
├── 13_flask_api.py                  # REST API endpoints
├── 14_ngrok_tunnel.py               # Ngrok tunnel setup
├── main.py                          # Entry point
├── README.md                        # This file
├── USAGE_GUIDE.md                   # Usage examples
└── MIGRATION_GUIDE.md               # Migration from notebook
```

## 🔧 Module Breakdown

### Core Pipeline Modules

1. **02_environment.py**
   - Environment variable loading from `.env`
   - Directory setup (data, output)
   - LangSmith tracing configuration

2. **03_llm_config.py**
   - Local LLM initialization (Llama models)
   - Text generation wrapper
   - CUDA/GPU detection

3. **04_data_models.py**
   - Pydantic models for input/output
   - Type validation and serialization

4. **05_clarification.py**
   - 2-step validation workflow
   - Input completeness checking
   - Automatic suggestion generation

5. **06_planning.py**
   - Research plan generation
   - Search step creation
   - Fallback plan handling

### Tool Integration Modules

6. **07_tavily_search.py**
   - Web search via Tavily API
   - Result parsing and retry logic
   - Source scoring

7. **08_react.py**
   - ReAct reasoning loop
   - Decision making for actions
   - Tool calling orchestration

### Post-Processing Modules

8. **09_evidence_processing.py**
   - Evidence deduplication
   - Source credibility scoring
   - DataFrame operations

9. **10_synthesis.py**
   - LLM-based report generation
   - 4 report sections generation
   - Citation management

10. **11_output_formatting.py**
    - Markdown report building
    - JSON serialization
    - Multi-format export

### Storage & Deployment Modules

11. **12_mongodb.py**
    - MongoDB connection management
    - Document storage
    - Report retrieval

12. **13_flask_api.py**
    - REST API endpoints
    - Streaming pipeline execution
    - CORS handling

13. **14_ngrok_tunnel.py**
    - Public URL exposure
    - Server launching

## 📋 Environment Variables

Required in `.env`:

```bash
# LLM & API Keys
LANGCHAIN_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
HUGGINGFACEHUB_API_TOKEN=hf_...
NGROK_AUTH_TOKEN=...

# LLM Configuration
STAGE_A_LOCAL_MODEL=meta-llama/Llama-3.2-3B-Instruct
STAGE_A_TEMPERATURE=0.2
STAGE_A_MAX_NEW_TOKENS=700
STAGE_A_DEVICE_MAP=auto

# Database
MONGO_URI=mongodb+srv://...

# Logging
STAGE_A_LOG_LEVEL=INFO
```

## 🚀 Quick Start

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Pipeline Mode

```bash
python stage_a/main.py pipeline \
  --prompt "Tìm hiểu thị trường xe điện tại Việt Nam" \
  --industry "Xe điện" \
  --market "Việt Nam"
```

### Server Mode (with ngrok)

```bash
python stage_a/main.py server --port 5000
```

## 📚 Usage Examples

### Python API

```python
from stage_a.02_environment import load_environment
from stage_a.03_llm_config import initialize_llm
from stage_a.04_data_models import StageAInput
from stage_a.05_clarification import clarify_user_prompt
from stage_a.06_planning import planner_chain
from stage_a.08_react import run_react_loop

# Initialize
config = load_environment()
llm = initialize_llm()

# Create input
input_data = StageAInput(
    user_prompt="Market research for AI startups",
    nganh_hang="AI/ML",
    thi_truong_muc_tieu="Southeast Asia"
)

# Run pipeline steps
clarification = clarify_user_prompt(llm, input_data.user_prompt, input_data)
plan = planner_chain(llm, clarification["clarified_input"])
react_result = run_react_loop(llm, plan)
```

### REST API

```bash
curl -X POST http://localhost:5000/api/research/stage_a \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Tìm hiểu thị trường xe điện",
    "nganh_hang": "Xe điện",
    "thi_truong_muc_tieu": "Việt Nam"
  }' \
  --no-buffer
```

## 📊 Output Formats

- **Markdown**: Full report with formatted sections and citations
- **JSON**: Structured data for programmatic use
- **MongoDB**: Persistent storage with metadata
- **Streaming**: Real-time progress via NDJSON

## 🔄 Pipeline Flow

```
Input → Clarification → Planning → ReAct Loop → Evidence Processing 
  → Synthesis → Formatting → Storage
```

## 🛠️ Development

### Run Tests

```bash
pytest stage_a/
```

### Code Structure

Each module is self-contained with:
- Clear imports
- Type hints
- docstrings
- Error handling
- Logging/output

### Adding New Modules

1. Create `NN_module_name.py`
2. Add import to `__init__.py`
3. Update main.py if needed
4. Document in README

## ⚙️ Configuration

### LLM Settings

Edit environment variables for model tuning:

```bash
STAGE_A_TEMPERATURE=0.2      # Lower = more deterministic
STAGE_A_MAX_NEW_TOKENS=700   # Max output length
```

### Search Settings

Configure Tavily search in code:

```python
tavily_search_with_retry(
    query=query,
    max_results=5,
    freshness="year",
    retries=3
)
```

## 📝 Logging

Real-time progress via `rich` output:

```python
from rich import print as rprint
rprint("[green]✅ Success[/green]")
rprint("[yellow]⚠️ Warning[/yellow]")
rprint("[red]✗ Error[/red]")
```

## 🤝 Integration Points

- **Frontend**: REST API at `/api/research/stage_a`
- **Database**: MongoDB for persistence
- **Public URL**: Ngrok tunnel exposure
- **Monitoring**: Health check at `/health`

## 📜 License

Same as parent project
