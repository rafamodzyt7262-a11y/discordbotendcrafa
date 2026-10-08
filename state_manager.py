import os
import json
import time
import random
from pathlib import Path
from dialogues import CONVERSATION_TOPICS

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = DATA_DIR / "shared_chat.json"


def get_conversation_state():
    if not STATE_FILE.exists():
        initial = {
            "turn": "bot1",
            "topic_index": 0,
            "step_index": 0,
            "is_paused": False,
            "timestamp": time.time()
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(initial, f)
        return initial

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"turn": "bot1", "topic_index": 0, "step_index": 0, "is_paused": False, "timestamp": time.time()}


def update_conversation_state(turn, topic_index, step_index, is_paused=False):
    state = {
        "turn": turn,
        "topic_index": topic_index,
        "step_index": step_index,
        "is_paused": is_paused,
        "timestamp": time.time()
    }
    temp = STATE_FILE.with_suffix(".tmp")
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(state, f)
    temp.replace(STATE_FILE)
