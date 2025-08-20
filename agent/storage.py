import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class Storage:
    """
    Super-simple JSONL storage. Good enough to validate flows.
    Later we can swap in a DB (SQLite/Postgres/Redis) behind the same API.
    """
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or os.getenv("DATA_DIR", "data"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.results_path = self.base_dir / "results.jsonl"

    # ---- writes --------------------------------------------------------------
    def save_result(self, record: Dict[str, Any]) -> None:
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        with self.results_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ---- reads ---------------------------------------------------------------
    def get_recent_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.results_path.exists():
            return []
        items: List[Dict[str, Any]] = []
        with self.results_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        continue
        return items[-limit:]

    # Backwards-compat name if needed by earlier code
    def load_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.get_recent_results(limit=limit)
