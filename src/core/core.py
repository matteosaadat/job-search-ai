from pathlib import Path
import yaml
from .config import JHConfig


class JHCore:
    def __init__(self, config: JHConfig):
        self.config = config
        self._boot()

    @property
    def truth_path(self) -> Path:
        return self.config.truth_path

    @property
    def blueprints_path(self) -> Path:
        return self.config.blueprints_path

    @property
    def rules_path(self) -> Path:
        return self.config.rules_path

    def _boot(self):
        self._ensure_path(self.truth_path, "Truth")
        self._ensure_path(self.blueprints_path, "Blueprints")
        self._ensure_path(self.config.data_path / "jobs", "Jobs")
        self._ensure_path(self.config.data_path / "companies", "Companies")
        self._ensure_path(self.config.data_path / "applications", "Applications")
        self._ensure_path(self.config.data_path / "rules", "Rules")
        self._ensure_path(self.config.config_dir / ".jh", "Runtime")

    def _ensure_path(self, path: Path, name: str):
        if not path.exists():
            path.mkdir(parents=True)
        elif not path.is_dir():
            raise NotADirectoryError(
                f"{name} path exists but is not a directory: {path}"
            )

    def load_rules(self) -> dict:
        rules_file = self.rules_path
        if not rules_file.exists():
            return {}
        with open(rules_file) as f:
            return yaml.safe_load(f) or {}

    @classmethod
    def from_config_file(cls, config_path: Path = None) -> "JHCore":
        config = JHConfig.load(config_path)
        return cls(config)
