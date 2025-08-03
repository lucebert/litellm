import asyncio
import time
from typing import Optional, Dict, Callable
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests: int, interval: float = 1.0):
        self.max_requests = max_requests
        self.interval = interval
        self.requests: Dict[float, int] = {}
        self._lock = asyncio.Lock()

    def _cleanup_old_requests(self, current_time: float) -> None:
        cutoff = current_time - self.interval
        self.requests = {ts: count for ts, count in self.requests.items() if ts > cutoff}

    async def acquire(self) -> None:
        async with self._lock:
            current_time = time.time()
            self._cleanup_old_requests(current_time)
            
            current_requests = sum(self.requests.values())
            if current_requests >= self.max_requests:
                sleep_time = min(self.requests.keys()) + self.interval - current_time
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.requests[current_time] = self.requests.get(current_time, 0) + 1

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await self.acquire()
            return await func(*args, **kwargs)
        return wrapper