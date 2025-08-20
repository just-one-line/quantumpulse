import threading
import time
from typing import Optional, Dict, Any

class TradingAgent:
    """
    Minimal background agent with start/stop + heartbeat.
    Keeps the interface stable for the Flask app.
    """

    def __init__(self, storage, config: Optional[Dict[str, Any]] = None):
        self.storage = storage
        self.config = config or {}
        self._interval = float(self.config.get("interval_seconds", 5))
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._iterations = 0
        self._last_heartbeat = None

    # ---------- public API used by app.py ----------

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            self._running = False

    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "interval_seconds": self._interval,
                "iterations": self._iterations,
                "last_heartbeat": self._last_heartbeat,
            }

    def update_config(self, new_config: Dict[str, Any]):
        with self._lock:
            if "interval_seconds" in new_config:
                try:
                    self._interval = max(1.0, float(new_config["interval_seconds"]))
                except Exception:
                    pass
            self.config.update(new_config)

    # ---------- internal loop ----------

    def _run_loop(self):
        while True:
            with self._lock:
                if not self._running:
                    break
            try:
                self._tick()
            except Exception as e:
                # Keep agent resilient; log to storage
                try:
                    self.storage.append_log(f"agent_error: {e}")
                except Exception:
                    pass
            time.sleep(self._interval)

    def _tick(self):
        # Do one unit of work; for now just heartbeat and counter
        self._iterations += 1
        self._last_heartbeat = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.storage.append_log("heartbeat")
        except Exception:
            pass
