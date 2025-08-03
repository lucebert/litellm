import time
import asyncio
from typing import Optional, Dict, Any, Callable
from functools import wraps
import hashlib
import json

class AsyncTTLCache:
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def _generate_key(self, *args, **kwargs) -> str:
        cache_key = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(cache_key.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if time.time() > entry["expiry"]:
            del self.cache[key]
            return None
        
        return entry["value"]

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self.cache[key] = {
                "value": value,
                "expiry": time.time() + self.ttl
            }

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = self._generate_key(*args, **kwargs)
            
            cached_result = await self.get(key)
            if cached_result is not None:
                return cached_result

            result = await func(*args, **kwargs)
            await self.set(key, result)
            return result

        return wrapper