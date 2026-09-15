from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("GAR_DATA_DIR", BASE_DIR / "data")).resolve()
GENERATED_DIR = DATA_DIR / "generated"
DB_PATH = DATA_DIR / "gar.sqlite3"

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "").strip()
CEREBRAS_API_BASE = os.getenv("CEREBRAS_API_BASE", "https://api.cerebras.ai/v1").rstrip("/")
DEFAULT_MODEL = os.getenv("GAR_DEFAULT_MODEL", "qwen-3.8-27b")
MAX_GENERATED_HTML_BYTES = int(os.getenv("GAR_MAX_HTML_BYTES", "1500000"))

# USD per token. Override through env if Cerebras pricing changes.
MODEL_PRICING = {
    "qwen-3.8-27b": {
        "input": float(os.getenv("GAR_QWEN_INPUT_USD_PER_TOKEN", "0.00000099")),
        "output": float(os.getenv("GAR_QWEN_OUTPUT_USD_PER_TOKEN", "0.00000149")),
    },
    "gpt-oss-120b": {
        "input": float(os.getenv("GAR_GPTOSS_INPUT_USD_PER_TOKEN", "0.00000035")),
        "output": float(os.getenv("GAR_GPTOSS_OUTPUT_USD_PER_TOKEN", "0.00000075")),
    },
}

SUPPORTED_MODELS = tuple(MODEL_PRICING.keys())

DATA_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
