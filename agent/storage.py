import os, sqlite3, json, time

DB_PATH = os.getenv("AGENT_DB", "agent.db")

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = _conn(); cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS signals(
        id TEXT PRIMARY KEY,
        symbol TEXT,
        ts INTEGER,
        label TEXT,
        confidence INTEGER,
        meta TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS proposals(
        id TEXT PRIMARY KEY,
        ts INTEGER,
        title TEXT,
        change_json TEXT,
        status TEXT
    )""")
    con.commit(); con.close()

def save_signal(sig: dict):
    con = _conn(); cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO signals VALUES(?,?,?,?,?,?)", (
        sig["id"],
        sig["symbol"],
        sig["ts"],
        sig["label"],
        sig["confidence"],
        json.dumps(sig.get("meta", {}))
    ))
    con.commit(); con.close()

def latest_signals(limit=20):
    con = _conn(); cur = con.cursor()
    cur.execute(
        "SELECT symbol, ts, label, confidence, meta FROM signals "
        "ORDER BY ts DESC LIMIT ?", (limit,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows

def save_proposal(pid: str, title: str, change: dict, status: str = "pending"):
    con = _conn(); cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO proposals VALUES(?,?,?,?,?)", (
        pid,
        int(time.time()),
        title,
        json.dumps(change),
        status
    ))
    con.commit(); con.close()
