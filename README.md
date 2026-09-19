# Alias Resolver

Keep shared paths, imports, and lifecycle calls in one reviewed YAML file.

Use one reviewed configuration to resolve project paths, Python imports, modules, and application lifecycle calls.

## See it work

**Input:** A supplied YAML file, a real synthetic data file, and three supplied lifecycle functions.

**Result:** The cache task completes, a deliberate startup failure is reported, and shutdown still closes the synthetic database task.

[Read the captured output](examples/result.txt) | [Inspect the example](examples/walkthrough.py)

Python 3.11 or newer. From the repository root:

```sh
python -m pip install -e .
python -m examples.walkthrough
```

The example uses synthetic material and runs offline. The captured output comes from executing this example, not a hand-written mockup.

## How it works

Path aliases resolve relative to the configuration file and cannot escape that root. Import and module aliases resolve lazily. Sequential lifecycle calls collect named results and failures, allowing the caller to decide how to handle a failed startup.

Implementation: [src/alias_resolver/resolver.py](src/alias_resolver/resolver.py), [src/alias_resolver/cli.py](src/alias_resolver/cli.py), [examples/config.yaml](examples/config.yaml).

## Limits

YAML import targets execute Python code and must be trusted. Daemon-thread startup reports thread launch, not eventual completion or failures inside the thread. This is not a service supervisor.

[Reference and CLI details](docs/REFERENCE.md) | [Origin](ORIGIN.md) | [Apache-2.0 license](LICENSE)
