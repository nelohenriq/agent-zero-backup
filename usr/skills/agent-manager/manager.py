
import os
import json
from datetime import datetime

AGENTS_DIR = "/a0/usr/custom_agents"

def create_agent(name, base_profile, context):
    """Create a new custom agent profile."""
    if not name or not base_profile:
        return {"status": "error", "message": "Name and base profile are required."}

    agent_file = os.path.join(AGENTS_DIR, f"{name}.json")

    if os.path.exists(agent_file):
        return {"status": "error", "message": f"Agent '{name}' already exists."}

    profile_data = {
        "name": name,
        "title": name.replace("_", " ").title(),
        "description": f"Custom agent based on {base_profile} profile.",
        "base_profile": base_profile,
        "context": context,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }

    with open(agent_file, "w") as f:
        json.dump(profile_data, f, indent=2)

    return {"status": "success", "message": f"Agent '{name}' created successfully.", "path": agent_file}

def list_agents():
    """List all custom agents."""
    agents = []
    if not os.path.exists(AGENTS_DIR):
        return agents

    for filename in os.listdir(AGENTS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(AGENTS_DIR, filename), "r") as f:
                agents.append(json.load(f))
    return agents

if __name__ == "__main__":
    # Demo execution
    print("Agent Manager module loaded.")
    print("Functions available: create_agent, list_agents")
