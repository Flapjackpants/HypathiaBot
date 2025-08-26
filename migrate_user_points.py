# migrate_user_points.py
import json
import redis
import os

# ---------------- CONFIG ----------------
JSON_FILE = "user_points.json"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # or set your password here
REDIS_KEY = "user_points"
# ----------------------------------------

# Connect to Redis
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# Load existing JSON
if not os.path.exists(JSON_FILE) or os.path.getsize(JSON_FILE) == 0:
    print("⚠️ JSON file not found or empty.")
    exit()

with open(JSON_FILE, "r") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ JSON file is corrupted.")
        exit()

# Convert keys/values to correct types
json_data = {str(k): int(v) for k, v in data.items()}

# Fetch existing keys from Redis
existing_keys = r.hkeys(REDIS_KEY)

# Filter out any keys that already exist in Redis
new_data = {k: v for k, v in json_data.items() if k not in existing_keys}

# Write only missing users to Redis
if new_data:
    r.hset(REDIS_KEY, mapping=new_data)
    print(f"✅ Migrated {len(new_data)} users to Redis.")
else:
    print("ℹ️ All users already exist in Redis. No migration needed.")
