from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml
from ..exceptions import LiteLLMException

@dataclass
class ModelConfig:
    model_type: str
    api_key_env: str
    base_url: Optional[str] = None
    timeout: float = 60.0
    max_retries: int = 3
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GlobalConfig:
    default_timeout: float = 60.0
    max_retries: int = 3
    cache_enabled: bool = False
    telemetry_enabled: bool = True
    log_level: str = "INFO"

class ConfigManager:
    def __init__(self):
        self._global_config = GlobalConfig()
        self._model_configs: Dict[str, ModelConfig] = {}
        
    @property
    def global_config(self) -> GlobalConfig:
        return self._global_config

    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        return self._model_configs.get(model_name)

    def load_config(self, config_path: str) -> None:
        path = Path(config_path)
        if not path.exists():
            raise LiteLLMException(f"Config file not found: {config_path}")

        try:
            if path.suffix == '.json':
                with open(path) as f:
                    config_data = json.load(f)
            elif path.suffix in ['.yml', '.yaml']:
                with open(path) as f:
                    config_data = yaml.safe_load(f)
            else:
                raise LiteLLMException(f"Unsupported config file format: {path.suffix}")

            # Load global config
            if 'global' in config_data:
                self._global_config = GlobalConfig(**config_data['global'])

            # Load model configs
            if 'models' in config_data:
                for model_name, model_config in config_data['models'].items():
                    self._model_configs[model_name] = ModelConfig(**model_config)
                    
        except Exception as e:
            raise LiteLLMException(f"Failed to load config: {str(e)}")

    def get_merged_config(self, model_name: str) -> Dict[str, Any]:
        """Get merged configuration for a model, combining global and model-specific settings."""
        config = {
            "timeout": self._global_config.default_timeout,
            "max_retries": self._global_config.max_retries,
            "cache_enabled": self._global_config.cache_enabled,
        }
        
        model_config = self.get_model_config(model_name)
        if model_config:
            config.update({
                "timeout": model_config.timeout,
                "max_retries": model_config.max_retries,
                **model_config.additional_params
            })
            
        return config