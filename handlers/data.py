# handlers/data.py
import redis
from collections import defaultdict

# Connect to Redis 
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

DEFAULT_POINTS = 80
REDIS_KEY = "user_points"

class RedisUserPoints(defaultdict):
    def __init__(self, default_factory, *args, **kwargs):
        super().__init__(default_factory, *args, **kwargs)
        self.load_from_redis()

    def load_from_redis(self):
        # Load all user points from Redis into the local dict.
        data = r.hgetall(REDIS_KEY)
        for k, v in data.items():
            self[int(k)] = int(v)

    def __getitem__(self, key):
        # Fallback to default if not in Redis.
        if key not in self:
            value = self.default_factory()
            self[key] = value
            r.hset(REDIS_KEY, key, value)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        # Update Redis whenever the dict is updated.
        r.hset(REDIS_KEY, key, value)
        super().__setitem__(key, value)

# Use the Redis-backed points system
user_points = RedisUserPoints(lambda: DEFAULT_POINTS)

# Other in-memory runtime-only data
last_message_time = {}
last_message_content = {}

def save_points():
    """Persist all user points back to Redis (not strictly needed, but useful)."""
    if user_points:
        r.hmset(REDIS_KEY, {str(k): v for k, v in user_points.items()})
