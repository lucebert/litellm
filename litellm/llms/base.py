from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, List
from dataclasses import dataclass
import httpx
from litellm.exceptions import LiteLLMException

@dataclass
class CompletionResult:
    text: str
    model: str
    usage: Dict[str, int]
    metadata: Dict[str, Any]

@dataclass
class EmbeddingResult:
    embeddings: List[List[float]]
    model: str
    usage: Dict[str, int]

class BaseLLM(ABC):
    def __init__(self, model_name: str):
        from ..utils.http_client import HTTPClientManager, ClientConfig
        from ..config.settings import ConfigManager

        self.model_name = model_name
        self._config_manager = ConfigManager()
        
        config = self._config_manager.get_merged_config(model_name)
        client_config = ClientConfig(
            timeout=config['timeout'],
            max_retries=config['max_retries']
        )
        self._http = HTTPClientManager(client_config)

    def __del__(self):
        if hasattr(self, '_http'):
            self._http.close()

    async def __aclose__(self):
        if hasattr(self, '_http'):
            await self._http.aclose()

    @property
    def http(self):
        return self._http

    @abstractmethod
    def validate_environment(self) -> None:
        """Validate and set up required environment for the model."""
        raise NotImplementedError

    @abstractmethod
    def completion(
        self,
        prompt: Union[str, List[str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> CompletionResult:
        """Generate completion for the given prompt."""
        raise NotImplementedError

    @abstractmethod
    def embedding(
        self,
        text: Union[str, List[str]],
        model: str,
        **kwargs
    ) -> EmbeddingResult:
        """Generate embeddings for the given text."""
        raise NotImplementedError

    def _handle_error(self, error: Exception) -> None:
        """Centralized error handling for LLM operations."""
        if isinstance(error, httpx.HTTPError):
            raise LiteLLMException(f"HTTP Error: {str(error)}")
        elif isinstance(error, TimeoutError):
            raise LiteLLMException("Request timed out")
        else:
            raise LiteLLMException(f"Unexpected error: {str(error)}")
