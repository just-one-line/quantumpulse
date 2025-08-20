import json
import os

STORAGE_FILE = "agent_data.json"

def load_data():
    """Load agent data from JSON file."""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return {"memory": []}

def save_data(data):
    """Save agent data to JSON file."""
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_memory(entry):
    """Add a new memory entry for the agent."""
    data = load_data()
    data["memory"].append(entry)
    save_data(data)

def get_memory(limit=10):
    """Retrieve the last `limit` memory entries."""
    data = load_data()
    return data["memory"][-limit:]
