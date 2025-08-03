from typing import Optional, Dict, Any
import httpx
from contextlib import contextmanager
from dataclasses import dataclass
from ..exceptions import LiteLLMException

@dataclass
class ClientConfig:
    timeout: float = 60.0
    max_retries: int = 3
    headers: Optional[Dict[str, str]] = None
    follow_redirects: bool = True

class HTTPClientManager:
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig()
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    @contextmanager
    def get_client(self):
        if self._sync_client is None:
            self._sync_client = self._create_client()
        try:
            yield self._sync_client
        except Exception as e:
            self._handle_client_error(e)

    async def get_async_client(self):
        if self._async_client is None:
            self._async_client = self._create_async_client()
        try:
            return self._async_client
        except Exception as e:
            self._handle_client_error(e)

    def _create_client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.config.timeout,
            headers=self.config.headers,
            follow_redirects=self.config.follow_redirects
        )

    def _create_async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.config.timeout,
            headers=self.config.headers,
            follow_redirects=self.config.follow_redirects
        )

    def _handle_client_error(self, error: Exception):
        if isinstance(error, httpx.TimeoutException):
            raise LiteLLMException("Request timed out") from error
        elif isinstance(error, httpx.NetworkError):
            raise LiteLLMException("Network error occurred") from error
        else:
            raise LiteLLMException(f"HTTP client error: {str(error)}") from error

    def close(self):
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        
    async def aclose(self):
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None