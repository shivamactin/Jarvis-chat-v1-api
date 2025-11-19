# kv_cache.py
import redis
import json
from typing import Any, Optional


class KVCache:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        prefix: str = "cache:"
    ):
        """Initialize Redis connection."""
        self.client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )
        self.prefix = prefix

    def _full_key(self, key: str) -> str:
        """Prefix keys to avoid collisions."""
        return f"{self.prefix}{key}"

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a key-value pair with optional expiration time (TTL in seconds)."""
        serialized = json.dumps(value)
        self.client.set(self._full_key(key), serialized, ex=ttl)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key. Returns None if not found."""
        val = self.client.get(self._full_key(key))
        return json.loads(val) if val else None

    def delete(self, key: str):
        """Delete key."""
        self.client.delete(self._full_key(key))

    def keys(self, pattern: str = "*") -> list[str]:
        """List all cached keys (with pattern matching)."""
        return self.client.keys(f"{self.prefix}{pattern}")
