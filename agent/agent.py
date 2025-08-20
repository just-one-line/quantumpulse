import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class TradingAgent:
    """
    A minimal agent that can create placeholder signals.
    Later we'll connect real data sources & strategy logic here.
    """

    def __init__(self, storage=None):
        self.storage = storage
        self._running = False
        self._last_run = None
        self._runs = 0

    def status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "last_run": self._last_run,
            "runs": self._runs,
        }

    # ---- public: run once ---------------------------------------------------
    def run_once(self) -> Dict[str, Any]:
        """
        Generate a placeholder signal and persist it.
        """
        now = datetime.now(timezone.utc).isoformat()
        signal = {
            "symbol": "BTCUSD",
            "time": now,
            "action": "HOLD",     # placeholder
            "confidence": 0.55,   # placeholder
            "price": 50000,       # placeholder
            "notes": "Stub signal; replace with real strategy outputs."
        }
        if self.storage:
            try:
                self.storage.save_result(signal)
            except Exception as e:
                signal["notes"] += f" (storage error: {e})"

        self._last_run = now
        self._runs += 1
        return signal

    # ---- optional: background loop (off by default) -------------------------
    def run_forever(self, interval_seconds: int = 300):
        """
        Simple loop. Only use when ENABLE_AGENT=1 to avoid unwanted background work.
        """
        self._running = True
        try:
            while self._running:
                self.run_once()
                time.sleep(interval_seconds)
        finally:
            self._running = False

    def stop(self):
        self._running = False
