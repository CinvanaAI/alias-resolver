from __future__ import annotations

import argparse
import json
from pathlib import Path

from .resolver import Resolver


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect YAML path/import/module aliases.")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("config", type=Path)
    path = commands.add_parser("resolve-path")
    path.add_argument("config", type=Path)
    path.add_argument("alias")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    resolver = Resolver.from_yaml(args.config)
    if args.command == "list":
        print(json.dumps(resolver.aliases(), indent=2))
    else:
        print(resolver.resolve_path(args.alias))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

