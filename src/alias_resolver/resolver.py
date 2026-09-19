from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
import threading
from typing import Any, Callable

import yaml


@dataclass(frozen=True)
class LifecycleResult:
    completed: tuple[str, ...]
    started_threads: tuple[str, ...]
    failures: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.failures


class Resolver:
    def __init__(self, config: dict[str, Any], root: Path) -> None:
        if not isinstance(config, dict):
            raise ValueError("Configuration root must be a mapping.")
        self.config = config
        self.root = root.resolve()

    @classmethod
    def from_yaml(cls, path: Path) -> "Resolver":
        config_path = path.expanduser().resolve()
        if not config_path.is_file():
            raise FileNotFoundError(config_path)
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        return cls(loaded or {}, config_path.parent)

    def aliases(self) -> dict[str, tuple[str, ...]]:
        startup = self._startup_config()
        return {
            "paths": tuple(sorted(self._mapping("paths", "aliases"))),
            "imports": tuple(sorted(self._mapping("imports"))),
            "modules": tuple(sorted(self._mapping("modules"))),
            "startup_sequential": tuple(startup.get("sequential", [])),
            "startup_threaded": tuple(startup.get("threaded", [])),
            "shutdown": tuple(self._shutdown_config()),
        }

    def resolve_path(self, alias: str) -> Path:
        relative = self._required(self._mapping("paths", "aliases"), alias, "Path")
        candidate = (self.root / relative).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise ValueError(f"Path alias escapes configured root: {alias}")
        return candidate

    def resolve_import(self, alias: str) -> Any:
        dotted = self._required(self._mapping("imports"), alias, "Import")
        if "." not in dotted:
            raise ValueError(f"Import alias must include a module and attribute: {alias}")
        module_name, attribute = dotted.rsplit(".", 1)
        return getattr(importlib.import_module(module_name), attribute)

    def resolve_module(self, alias: str) -> Any:
        dotted = self._required(self._mapping("modules"), alias, "Module")
        return importlib.import_module(dotted)

    def run_startup_tasks(self) -> LifecycleResult:
        startup = self._startup_config()
        completed: list[str] = []
        threaded: list[str] = []
        failures: list[str] = []
        for name in startup.get("sequential", []):
            self._run_one(name, completed, failures)
        for name in startup.get("threaded", []):
            try:
                function = self._callable(name)
                thread = threading.Thread(target=function, name=f"alias:{name}", daemon=True)
                thread.start()
                threaded.append(name)
            except Exception as exc:
                failures.append(f"{name}: {exc}")
        return LifecycleResult(tuple(completed), tuple(threaded), tuple(failures))

    def run_shutdown_tasks(self) -> LifecycleResult:
        completed: list[str] = []
        failures: list[str] = []
        for name in self._shutdown_config():
            self._run_one(name, completed, failures)
        return LifecycleResult(tuple(completed), (), tuple(failures))

    def _run_one(self, name: str, completed: list[str], failures: list[str]) -> None:
        try:
            self._callable(name)()
            completed.append(name)
        except Exception as exc:
            failures.append(f"{name}: {exc}")

    def _callable(self, name: str) -> Callable[[], Any]:
        value = self.resolve_import(name)
        if not callable(value):
            raise TypeError(f"Configured import is not callable: {name}")
        return value

    def _mapping(self, *keys: str) -> dict[str, str]:
        value: Any = self.config
        for key in keys:
            if not isinstance(value, dict):
                return {}
            value = value.get(key, {})
        if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in value.items()):
            raise ValueError(f"Configuration section {'.'.join(keys)} must map strings to strings.")
        return value

    def _startup_config(self) -> dict[str, list[str]]:
        value = self.config.get("background_tasks", {}).get("on_startup", {})
        if not isinstance(value, dict):
            raise ValueError("background_tasks.on_startup must be a mapping.")
        normalized = {
            "sequential": value.get("sequential", value.get("non-thread", [])),
            "threaded": value.get("threaded", value.get("threading", [])),
        }
        for key, tasks in normalized.items():
            if not isinstance(tasks, list) or not all(isinstance(task, str) for task in tasks):
                raise ValueError(f"Startup group {key} must be a list of import aliases.")
        return normalized

    def _shutdown_config(self) -> list[str]:
        value = self.config.get("background_tasks", {}).get("on_shutdown", [])
        if not isinstance(value, list) or not all(isinstance(task, str) for task in value):
            raise ValueError("background_tasks.on_shutdown must be a list of import aliases.")
        return value

    @staticmethod
    def _required(mapping: dict[str, str], alias: str, kind: str) -> str:
        if alias not in mapping:
            raise KeyError(f"{kind} alias {alias!r} not found. Available: {sorted(mapping)}")
        return mapping[alias]

