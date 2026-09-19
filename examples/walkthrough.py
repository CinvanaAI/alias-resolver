"""Resolve actual aliases and observe successful and failed lifecycle calls."""
import json
from dataclasses import asdict
from pathlib import Path
from alias_resolver import Resolver
from examples import lifecycle_tasks

resolver = Resolver.from_yaml(Path(__file__).with_name("lifecycle.yaml"))
startup = resolver.run_startup_tasks()
resolved = resolver.resolve_path("data_file")
module = resolver.resolve_module("tasks")
imported = resolver.resolve_import("warm_cache")
shutdown = resolver.run_shutdown_tasks()
assert startup.completed == ("warm_cache",)
assert len(startup.failures) == 1 and "synthetic startup failure" in startup.failures[0]
assert shutdown.ok and lifecycle_tasks.events == ["cache warmed", "startup failed", "database closed"]
print(json.dumps({
    "path": resolved.relative_to(resolver.root).as_posix(),
    "input": json.loads(resolved.read_text()),
    "import_matches_module": imported is module.warm_cache,
    "startup": asdict(startup), "shutdown": asdict(shutdown),
    "events": lifecycle_tasks.events,
}, indent=2))
