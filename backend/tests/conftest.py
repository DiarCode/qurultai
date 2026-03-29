from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("OPENAI_TIMEOUT_SECONDS", "8")
os.environ.setdefault("ENABLE_LLM_CALLS", "false")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
