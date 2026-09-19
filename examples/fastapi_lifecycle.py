from contextlib import asynccontextmanager
from pathlib import Path

from alias_resolver import Resolver


resolver = Resolver.from_yaml(Path("config.yaml"))


@asynccontextmanager
async def lifespan(_app):
    startup = resolver.run_startup_tasks()
    if not startup.ok:
        raise RuntimeError(startup.failures)
    yield
    shutdown = resolver.run_shutdown_tasks()
    if not shutdown.ok:
        raise RuntimeError(shutdown.failures)

