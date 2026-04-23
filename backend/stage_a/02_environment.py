"""
Environment Configuration & Loading
Handles .env loading and LangSmith tracing setup
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from rich import print as rprint


def load_environment(env_path: str = None) -> dict:
    """Load environment variables from .env file"""
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    required_keys = ["LANGCHAIN_API_KEY", "TAVILY_API_KEY"]
    missing = [k for k in required_keys if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing required env keys: {missing}")

    # Setup LangSmith tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "Stage-A-Market-Research-Local"

    rprint("[green]Environment loaded. LANGCHAIN + TAVILY keys are available.[/green]")
    return {
        "langchain_api_key": os.getenv("LANGCHAIN_API_KEY"),
        "tavily_api_key": os.getenv("TAVILY_API_KEY"),
        "huggingface_token": os.getenv("HUGGINGFACEHUB_API_TOKEN", "hf.."),
        "ngrok_token": os.getenv("NGROK_AUTH_TOKEN"),
        "mongo_uri": os.getenv("MONGO_URI"),
    }


def setup_directories() -> dict:
    """Create and return output directories"""
    base_dir = Path.cwd()
    data_dir = base_dir / "data"
    output_dir = base_dir / "outputs"
    
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "base": base_dir,
        "data": data_dir,
        "output": output_dir,
    }


if __name__ == "__main__":
    config = load_environment()
    dirs = setup_directories()
    print("Environment and directories initialized successfully")
