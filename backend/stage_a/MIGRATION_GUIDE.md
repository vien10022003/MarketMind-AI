# Migration Guide - From Notebook to Python Modules

Guide for migrating from the Jupyter notebook `A_stage_local_marketing_agen-v2.ipynb` to the modularized Python package.

## 🔄 Before & After

### Before (Notebook Cell 1-29)

```python
# Everything in one Jupyter notebook
# Cells mixed across thousands of lines
# Hard to reuse, test, or maintain
# Installation sprawled across first cell
# Config scattered throughout
```

### After (Modular Package)

```python
from stage_a.main import run_pipeline

output = run_pipeline("Your research question")
# Clean, simple, production-ready
```

## 📋 Mapping Notebook Cells to Modules

| Old Location | New Module | Purpose |
|---|---|---|
| Cell 1-2 | `02_environment.py`, `main.py` | Setup & dependencies |
| Cell 3-4 | `02_environment.py` | .env loading |
| Cell 5-6 | `03_llm_config.py` | LLM initialization |
| Cell 7-9 | `04_data_models.py` | Data structures |
| Cell 10-15 | `05_clarification.py` | Input validation |
| Cell 16-17 | `06_planning.py` | Research planning |
| Cell 18-19 | `07_tavily_search.py` | Web search |
| Cell 20-21 | `08_react.py` | ReAct loop |
| Cell 22-23 | `09_evidence_processing.py` | Evidence filtering |
| Cell 24-25 | `10_synthesis.py` | Report generation |
| Cell 26 | `11_output_formatting.py` | Output formatting |
| Cell 27 | `12_mongodb.py` | Database storage |
| Cell 28-29 | `13_flask_api.py`, `14_ngrok_tunnel.py` | API & deployment |

## 🚀 Migration Scenarios

### Scenario 1: Simple Usage (Terminal)

**Before:**
```bash
# Open Jupyter, run all cells, modify notebook, re-run
jupyter notebook A_stage_local_marketing_agen-v2.ipynb
```

**After:**
```bash
# Run from command line
python stage_a/main.py pipeline \
  --prompt "Your research topic" \
  --industry "Industry" \
  --market "Market"
```

### Scenario 2: Python Script Usage

**Before:**
```python
# Export notebook as .py, manually edit imports
# Then use it (fragile, version issues)
from A_stage_local_marketing_agen_v2 import *
```

**After:**
```python
from stage_a.main import run_pipeline

output = run_pipeline("Research topic")
print(output.tong_quan_thi_truong)
```

### Scenario 3: Server/API Usage

**Before:**
```python
# Use nbconvert + custom wrapper
# Embed Jupyter kernel in Flask (heavy, risky)
from nbconvert import ...
```

**After:**
```bash
# Direct Flask integration
python stage_a/main.py server --port 5000
```

### Scenario 4: Unit Testing

**Before:**
```bash
# Hard to test Jupyter notebooks
# nbval, pytest not ideal
```

**After:**
```bash
# Test each module independently
pytest stage_a/test_planning.py
pytest stage_a/test_synthesis.py
```

## 🔧 API Compatibility

### Old Notebook API

```python
# Direct access to globals
llm.generate(prompt)
plan = planner_chain(research_input, max_steps=8)
evidence_df = normalize_and_filter_evidence(items)
stage_a_output = synthesize_stage_a_report(research_input, df)
```

### New Module API

```python
from stage_a.03_llm_config import LocalTextGenerator
from stage_a.06_planning import planner_chain
from stage_a.09_evidence_processing import normalize_and_filter_evidence
from stage_a.10_synthesis import synthesize_stage_a_report

llm = LocalTextGenerator(config)
llm.generate(prompt)
plan = planner_chain(llm, research_input, max_steps=8)
evidence_df = normalize_and_filter_evidence(items)
stage_a_output = synthesize_stage_a_report(llm, research_input, df)
```

**Key Changes:**
- Functions now require `llm` instance (dependency injection)
- Explicit imports instead of implicit globals
- Better error handling and type hints

## 🔀 Code Translation Examples

### Example 1: Initialization

**Notebook:**
```python
# Cell 1
from google.colab import drive
drive.mount('/content/drive')
!pip install pydantic==2.10.3
# ... (20+ lines of install)

# Cell 3-4
load_dotenv("/content/drive/MyDrive/.env")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
```

**Modules:**
```python
# One line
from stage_a.02_environment import load_environment
config = load_environment()
```

### Example 2: Research Pipeline

**Notebook:**
```python
# Cells scattered, hard to follow
llm_cfg = LocalLLMConfig()
local_llm = LocalTextGenerator(llm_cfg)

user_input = StageAInput(user_prompt="...")
clarification_result = clarify_user_prompt_with_two_step_validation(...)
plan = planner_chain(user_input)
react_state = run_react_loop(plan)
evidence_df = normalize_and_filter_evidence(react_state["evidence"])
stage_a_output = synthesize_stage_a_report(user_input, evidence_df)
```

**Modules:**
```python
# Clean, documented flow
from stage_a.main import run_pipeline

output = run_pipeline(
    user_prompt="...",
    industry="...",
    market="..."
)
```

### Example 3: API Streaming

**Notebook:**
```python
# Cell 28-29 (complex, intertwined)
def run_stage_a_pipeline_generator(req_data: dict):
    yield json.dumps({...}) + "\n"
    # ... (200+ lines)

@app.route('/api/research/stage_a', methods=['POST'])
def api_research_stage_a():
    return Response(stream_with_context(...), ...)
```

**Modules:**
```python
# Separated concerns
# stage_a/13_flask_api.py
def run_stage_a_pipeline_generator(req_data: dict):
    # Cleaner, focused on pipeline logic
    pass

@app.route('/api/research/stage_a', methods=['POST'])
def api_research_stage_a():
    # Clean routing
    pass

# stage_a/14_ngrok_tunnel.py
def setup_ngrok_tunnel(port=5000):
    # Tunnel logic isolated
    pass
```

## 📚 Dependency Management

### Notebook Approach

```python
# Cell 1: Hard to track, potential conflicts
!pip install pandas==2.2.2
!pip install pydantic==2.10.3
!pip install langchain==0.3.11 langchain-community==0.3.5
# ... (20+ pip install lines mixed in)
```

### Module Approach

```bash
# requirements.txt (centralized)
pydantic==2.10.3
langchain==0.3.11
langchain-community==0.3.5
pandas==2.2.2
# ... (all in one place)

# Install once
pip install -r requirements.txt
```

## 🔌 Integration Points

### Frontend Communication

**Before:**
```javascript
// Frontend had to call ngrok URL directly
fetch('https://ngrok-url.com/api/research/stage_a', {...})
```

**After:**
```javascript
// Same API, now modular and maintainable
fetch('https://api.example.com/api/research/stage_a', {...})

// Or local development
fetch('http://localhost:5000/api/research/stage_a', {...})
```

### Database Interaction

**Before:**
```python
# Cell 27: MongoDB scattered in notebook
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client['marketmind_ai']
# ... manual operations inline
```

**After:**
```python
# Encapsulated class
from stage_a.12_mongodb import MongoDBManager

mongo = MongoDBManager(config["mongo_uri"])
mongodb_id = mongo.save_report(metadata, output)
```

## ✅ Checklist for Migration

- [ ] Replace Jupyter execution with Python script calls
- [ ] Update imports to use new modules
- [ ] Update function signatures (add `llm` parameter)
- [ ] Move configuration to `.env`
- [ ] Test each module independently
- [ ] Update API client URLs if deployed
- [ ] Archive old notebook as backup
- [ ] Update documentation

## 🎯 Benefits After Migration

| Benefit | Before | After |
|---|---|---|
| **Reusability** | Hard (globals) | Easy (imports) |
| **Testing** | Limited (nbval) | Full (pytest) |
| **Deployment** | Complex (nbconvert) | Simple (Flask) |
| **Maintenance** | Difficult (scattered) | Easy (modular) |
| **Performance** | Slow (notebook overhead) | Fast (native Python) |
| **IDE Support** | Limited | Full |
| **Version Control** | Difficult (JSON cells) | Easy (.py files) |
| **Collaboration** | Hard (notebook conflicts) | Easy (git merge) |

## 🚨 Common Migration Issues

### Issue 1: Type Mismatch

**Error:**
```
TypeError: planner_chain() missing 1 required positional argument: 'llm'
```

**Fix:**
```python
# Before
plan = planner_chain(research_input)

# After
from stage_a.03_llm_config import initialize_llm
llm = initialize_llm()
plan = planner_chain(llm, research_input)
```

### Issue 2: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'stage_a'
```

**Fix:**
```bash
# Ensure you're running from backend directory
cd backend
python stage_a/main.py pipeline --prompt "..."

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

### Issue 3: Configuration Not Found

**Error:**
```
EnvironmentError: Missing required env keys: ['LANGCHAIN_API_KEY']
```

**Fix:**
```bash
# Ensure .env exists in working directory
ls -la .env

# Or specify path
export STAGE_A_ENV=/path/to/.env
python stage_a/main.py pipeline --prompt "..."
```

## 🔗 Further Reading

- [README.md](README.md) - Module overview
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - Detailed usage examples
- Individual module docstrings

## 🎓 Learning Path

1. **Understand the structure**: Read `README.md`
2. **Try simple example**: `python stage_a/main.py pipeline --prompt "..."`
3. **Run as server**: `python stage_a/main.py server`
4. **Explore modules**: Read individual module code
5. **Customize**: Modify modules for your use case
6. **Deploy**: Use Flask + Ngrok for production

---

**Migration completed!** You now have a production-ready, maintainable Python package instead of a Jupyter notebook.
