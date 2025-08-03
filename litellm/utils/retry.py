import asyncio
from functools import wraps
from typing import Type, Tuple, Optional, Callable, Any
import random

class RetryHandler:
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exceptions = exceptions
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        delay = min(self.base_delay * (2 ** (attempt - 1)), self.max_delay)
        if self.jitter:
            delay *= random.uniform(0.5, 1.5)
        return delay

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except self.exceptions as e:
                    attempt += 1
                    if attempt >= self.max_retries:
                        raise e
                    
                    delay = self.calculate_delay(attempt)
                    await asyncio.sleep(delay)