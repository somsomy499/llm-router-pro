"""LRU cache for LLM responses to avoid redundant API calls."""
import hashlib
import json
import time
import threading
from collections import OrderedDict
from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class CacheEntry:
    key: str
    value: Any
    created_at: float
    ttl: float
    hit_count: int = 0
    
    @property
    def is_expired(self):
        return time.time() - self.created_at > self.ttl

class ResponseCache:
    """Thread-safe LRU cache for LLM responses."""
    
    def __init__(self, maxsize: int = 1000, default_ttl: float = 3600):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def _make_key(self, messages, model, **kwargs):
        raw = json.dumps({"m": messages, "model": model, **kwargs}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def get(self, messages, model, **kwargs) -> Optional[Any]:
        key = self._make_key(messages, model, **kwargs)
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired:
                    entry.hit_count += 1
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry.value
                else:
                    del self._cache[key]
            self._misses += 1
        return None
    
    def set(self, messages, model, value, ttl=None, **kwargs):
        key = self._make_key(messages, model, **kwargs)
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self.maxsize:
                self._cache.popitem(last=False)
            self._cache[key] = CacheEntry(
                key=key, value=value,
                created_at=time.time(),
                ttl=ttl or self.default_ttl
            )
    
    def invalidate(self, messages, model, **kwargs):
        key = self._make_key(messages, model, **kwargs)
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    @property
    def hit_rate(self):
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0
    
    @property
    def stats(self):
        return {
            "size": len(self._cache),
            "maxsize": self.maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{self.hit_rate:.1%}",
        }
