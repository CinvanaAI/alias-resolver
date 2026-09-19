# Alias Resolver

A small YAML-driven utility for centralizing project-relative paths, dynamic Python imports, and startup/shutdown task groups.

## Why it exists

Applications often accumulate hardcoded paths and dotted import strings across entrypoints. Alias Resolver keeps those values in one reviewed configuration while providing a narrow API for resolving them.

## Install

```powershell
python -m pip install -e ".[test]"
```

## Configuration

```yaml
paths:
  aliases:
    data_file: data/input.json

imports:
  warm_cache: examples.lifecycle_tasks.warm_cache
  close_database: examples.lifecycle_tasks.close_database

modules:
  tasks: examples.lifecycle_tasks

background_tasks:
  on_startup:
    sequential: [warm_cache]
    threaded: []
  on_shutdown: [close_database]
```

## Use

```python
from pathlib import Path
from alias_resolver import Resolver

resolver = Resolver.from_yaml(Path("examples/lifecycle.yaml"))
data_file = resolver.resolve_path("data_file")
warm_cache = resolver.resolve_import("warm_cache")
tasks_module = resolver.resolve_module("tasks")
```

Run configured lifecycle tasks:

```python
startup = resolver.run_startup_tasks()
shutdown = resolver.run_shutdown_tasks()
```

Sequential task failures and thread-launch failures appear in the returned result. Exceptions raised later inside daemon threads are not captured by that result.

Inspect a configuration without importing anything:

```powershell
alias-resolver list config.yaml
alias-resolver resolve-path config.yaml data_file
```

## Security boundary

- Resolved filesystem aliases must remain inside the configured project root.
- Dynamic imports execute Python import side effects. Treat the YAML file as trusted code configuration, not untrusted user input.
- Threaded startup tasks are daemon threads; callers remain responsible for application-level lifecycle coordination.

## When not to use it

For a small application with one entrypoint, direct imports and ordinary
`pathlib` constants are usually clearer. This utility is aimed at projects
where several reviewed entrypoints need the same path/import/lifecycle aliases;
it is not a dependency-injection framework or a safe interpreter for
user-supplied configuration.

## Test

```powershell
python -m pytest
```

Licensed under Apache-2.0. See `ORIGIN.md` for the extraction boundary.
