# Origin

This repository refreshes an earlier Apache-licensed utility that centralized project-relative paths, dynamic imports, and startup/shutdown task aliases in a YAML file.

The public snapshot preserves the original purpose while replacing package-relative hidden configuration with an explicit `Resolver`, adding path-containment checks, configuration validation, a CLI, lifecycle result reporting, packaging, and tests. The original FastAPI demonstration is retained as an example rather than making FastAPI a runtime dependency.

