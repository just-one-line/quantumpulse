import threading
import time
from datetime import datetime, timezone

# simple in-memory config & state
_config = {
    "interval_seconds": 5
}
_state = {
    "running": False,
    "started_at": None,
    "last_heartbeat": None,
    "iterations": 0,
    "message": "idle"
}
_logs = []
_lock = threading.Lock()
_worker_thread = None

def _log(line: str):
    with _lock:
        ts = datetime.now(timezone.utc).isoformat()
        _logs.append(f"[{ts}] {line}")
        # keep logs bounded
        if len(_logs) > 2000:
            del _logs[: len(_logs) - 2000]

def _tick():
    """One iteration of the agent work. Extend this later with real fetch/analyze."""
    # placeholder work: simulate doing something useful
    time.sleep(0.01)

def _loop():
    _log("Agent loop started.")
    try:
        while True:
            with _lock:
                if not _state["running"]:
                    _log("Agent loop stopping.")
                    break
                _state["iterations"] += 1
                _state["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
            _tick()
            time.sleep(max(1, int(_config.get("interval_seconds", 5))))
    except Exception as e:
        _log(f"Agent error: {e!r}")
        with _lock:
            _state["running"] = False
            _state["message"] = f"error: {e!r}"
    finally:
        with _lock:
            if _state["running"]:
                _state["running"] = False

def status():
    with _lock:
        return {
            "state": "running" if _state["running"] else "stopped",
            "started_at": _state["started_at"],
            "last_heartbeat": _state["last_heartbeat"],
            "iterations": _state["iterations"],
            "message": _state["message"],
            "interval_seconds": _config.get("interval_seconds", 5),
        }

def get_logs(limit: int = 200):
    with _lock:
        return _logs[-limit:]

def set_config(cfg: dict):
    with _lock:
        _config.update({k: v for k, v in cfg.items() if v is not None})
    _log(f"Config updated: {cfg}")

def get_config():
    with _lock:
        return dict(_config)

def start():
    global _worker_thread
    with _lock:
        if _state["running"]:
            _log("Start called but agent already running.")
            return True
        _state.update({
            "running": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "message": "running"
