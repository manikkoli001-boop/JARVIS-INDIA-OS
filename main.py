from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import os
from ddgs import DDGS

app = FastAPI()

# =========================
# MEMORY SYSTEM
# =========================
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# =========================
# REQUEST MODEL
# =========================
class Query(BaseModel):
    message: str

# =========================
# INTERNET SEARCH
# =========================
def internet_search(query):
    results = []
    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=3)
        for r in search_results:
            results.append(r["body"])
    return "\n".join(results)

# =========================
# AI AGENT
# =========================
@app.post("/agent")
def run_agent(query: Query):
    user_message = query.message.lower()
    memory = load_memory()

    # =========================
    # SAVE NAME
    # =========================
    if "my name is" in user_message:
        name = user_message.replace("my name is", "").strip()
        memory["name"] = name
        save_memory(memory)
        return {
            "reply": f"Nice to meet you, {name}. I will remember your name permanently."
        }

    # =========================
    # TELL NAME
    # =========================
    if "what is my name" in user_message:
        if "name" in memory:
            return {
                "reply": f"Your name is {memory['name']}."
            }
        else:
            return {
                "reply": "I don't know your name yet."
            }

    # =========================
    # PERMANENT MEMORY
    # =========================
    if "remember that" in user_message:
        info = user_message.replace("remember that", "").strip()
        if "memories" not in memory:
            memory["memories"] = []
        memory["memories"].append(info)
        save_memory(memory)
        return {
            "reply": "Done. I will remember that permanently."
        }

    # =========================
    # SHOW MEMORIES
    # =========================
    if "what do you remember about me" in user_message:
        memories = memory.get("memories", [])
        if memories:
            return {
                "reply": "Here is what I remember about you: " + ", ".join(memories)
            }
        else:
            return {
                "reply": "I do not remember anything yet."
            }

    # =========================
    # INTERNET SEARCH
    # =========================
    if "search" in user_message or "latest" in user_message or "news" in user_message:
        search_data = internet_search(user_message)
        return {
            "reply": f"Here is what I found:\n\n{search_data}"
        }

    # =========================
    # NORMAL CHAT
    # =========================
    return {
        "reply": f"You said: {query.message}"
    }
