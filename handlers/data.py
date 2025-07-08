# handlers/data.py
from collections import defaultdict
import os
import json

def load_user_points():
    if os.path.exists("user_points.json") and os.path.getsize("user_points.json") > 0:
        try:
            with open("user_points.json", "r") as f:
                data = json.load(f)
                return defaultdict(lambda: 80, {int(k): int(v) for k, v in data.items()})
        except json.JSONDecodeError:
            print("⚠️ Corrupted JSON file. Starting fresh.")
    return defaultdict(lambda: 80)

user_points = load_user_points()
last_message_time = {}
last_message_content = {}

def save_points():
    with open("user_points.json", "w") as f:
        json.dump(user_points, f)
