from pathlib import Path
import yaml


class JHConfig:
    def __init__(self, data: dict, config_dir: Path):
        self._data = data
        self.config_dir = config_dir

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def require(self, key: str):
        if key not in self._data:
            raise ValueError(f"Missing required config key: '{key}'")
        return self._data[key]

    def get_ai_provider(self, name: str = None) -> dict:
        providers = self._data.get("ai-providers", {})
        if providers:
            key = name or self._data.get("ai-default")
            if not key:
                raise ValueError(
                    "'ai-default' not set in job-hunt.config.yaml.\n"
                    f"Available providers: {', '.join(providers)}"
                )
            if key not in providers:
                raise ValueError(
                    f"AI provider '{key}' not found in ai-providers.\n"
                    f"Available: {', '.join(providers)}"
                )
            entry = providers[key]
            return {
                "name": key,
                "provider": entry.get("provider", "anthropic"),
                "model": entry["model"],
                "api-key": entry.get("api-key", ""),
            }
        return {
            "name": "default",
            "provider": self._data.get("ai-provider", "anthropic"),
            "model": self._data.get("ai-model", ""),
            "api-key": self._data.get("api-key", ""),
        }

    def list_ai_providers(self) -> list[str]:
        providers = self._data.get("ai-providers", {})
        return list(providers.keys()) if providers else ["default"]

    @property
    def ai_provider(self) -> str:
        return self.get_ai_provider()["provider"]

    @property
    def ai_model(self) -> str:
        return self.get_ai_provider()["model"]

    @property
    def api_key(self) -> str:
        return self.get_ai_provider()["api-key"]

    @property
    def data_path(self) -> Path:
        return (self.config_dir / self._data.get("data-path", "data-storage")).resolve()

    @property
    def truth_path(self) -> Path:
        return (self.data_path / self.require("truth-path")).resolve()

    @property
    def blueprints_path(self) -> Path:
        return (self.data_path / self.require("blueprints-path")).resolve()

    @property
    def rules_path(self) -> Path:
        rules = self._data.get("rules-path", "rules/config.yaml")
        return (self.data_path / rules).resolve()

    def resolve(self, p) -> Path:
        return (self.config_dir / Path(p)).resolve()

    @classmethod
    def find_config(cls, start: Path = None) -> Path:
        current = (start or Path.cwd()).resolve()
        for directory in [current, *current.parents]:
            candidate = directory / "job-hunt.config.yaml"
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            "No job-hunt.config.yaml found in this directory or any parent."
        )

    @classmethod
    def load(cls, config_path: Path = None) -> "JHConfig":
        if config_path is None:
            config_path = cls.find_config()

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            raw = yaml.safe_load(f)

        if not raw:
            raise ValueError("job-hunt.config.yaml is empty.")

        for key in ["truth-path", "blueprints-path"]:
            if key not in raw:
                raise ValueError(f"job-hunt.config.yaml missing required key: '{key}'")

        has_flat = "ai-model" in raw and "api-key" in raw
        has_providers = "ai-providers" in raw
        if not has_flat and not has_providers:
            raise ValueError(
                "job-hunt.config.yaml must define AI config.\n"
                "Use ai-providers (new) or ai-model + api-key (legacy)."
            )

        return cls(raw, config_path.parent.resolve())
