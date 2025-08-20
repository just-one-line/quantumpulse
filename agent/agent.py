import threading
import time
from datetime import datetime, timezone

# In-memory config/state/logs
_config = {"interval_seconds": 5}
_state = {
    "running": False,
    "started_at": None,
    "last_heartbeat": None,
    "iterations": 0,
    "message": "idle",
}
_logs = []
_lock = threading.Lock()
_worker_thread = None


def _log(line):
    """Append a timestamped line to the circular log buffer."""
    ts = datetime.now(timezone.utc).isoformat()
    line_out = "[" + ts + "] " + str(line)
    with _lock:
        _logs.append(line_out)
        # Keep at most 2000 lines
        if len(_logs) > 2000:
            del _logs[: len(_logs) - 2000]


def _tick():
    """One unit of work. Replace later with real fetch/analyze."""
    # simulate doing something tiny
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
            # read interval outside lock
            interval = _config.get("interval_seconds", 5)
            try:
                interval = int(interval)
            except Exception:
                interval = 5
            if interval < 1:
                interval = 1
            time.sleep(interval)
    except Exception as e:
        _log("Agent error: " + repr(e))
        with _lock:
            _state["running"] = False
            _state["message"] = "error: " + repr(e)
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


def get_logs(limit=200):
    with _lock:
        try:
            limit = int(limit)
        except Exception:
            limit = 200
        return _logs[-limit:]


def set_config(cfg):
    if not isinstance(cfg, dict):
        return
    with _lock:
        for k, v in cfg.items():
            if v is not None:
                _config[k] = v
    _log("Config updated: " + repr(cfg))


def get_config():
    with _lock:
        return dict(_config)


def start():
    global _worker_thread
    with _lock:
        if _state["running"]:
            _log("Start called but agent already running.")
            return True
        _state["running"] = True
        _state["started_at"] = datetime.now(timezone.utc).isoformat()
        _state["message"] = "running"
        _worker_thread = threading.Thread(target=_loop, daemon=True)
        _worker_thread.start()
    return True


def stop():
    with _lock:
        if not _state["running"]:
            _log("Stop called but agent already stopped.")
            return True
        _state["running"] = False
        _state["message"] = "stopping"
    return True
