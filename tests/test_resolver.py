from pathlib import Path

import pytest

from alias_resolver import Resolver


def test_loads_yaml_and_resolves_contained_path(tmp_path: Path) -> None:
    config = tmp_path / "config.yaml"
    config.write_text("paths:\n  aliases:\n    data: data/input.json\n", encoding="utf-8")
    resolver = Resolver.from_yaml(config)
    assert resolver.resolve_path("data") == (tmp_path / "data" / "input.json").resolve()


def test_rejects_path_escape(tmp_path: Path) -> None:
    resolver = Resolver({"paths": {"aliases": {"bad": "../private.txt"}}}, tmp_path)
    with pytest.raises(ValueError, match="escapes"):
        resolver.resolve_path("bad")


def test_missing_alias_lists_available_values(tmp_path: Path) -> None:
    resolver = Resolver({"paths": {"aliases": {"known": "known.txt"}}}, tmp_path)
    with pytest.raises(KeyError, match="known"):
        resolver.resolve_path("missing")


def test_resolves_import_and_module(tmp_path: Path) -> None:
    resolver = Resolver(
        {"imports": {"sqrt": "math.sqrt"}, "modules": {"math": "math"}},
        tmp_path,
    )
    assert resolver.resolve_import("sqrt")(9) == 3
    assert resolver.resolve_module("math").sqrt(16) == 4


def test_rejects_non_mapping_configuration(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="mapping"):
        Resolver([], tmp_path)  # type: ignore[arg-type]


def test_supports_original_lifecycle_group_names(tmp_path: Path) -> None:
    resolver = Resolver(
        {
            "imports": {"noop": "tests.fixtures.noop"},
            "background_tasks": {"on_startup": {"non-thread": [], "threading": []}},
        },
        tmp_path,
    )
    assert resolver.run_startup_tasks().ok


def test_shutdown_reports_failures(tmp_path: Path) -> None:
    resolver = Resolver(
        {
            "imports": {"bad": "math.missing"},
            "background_tasks": {"on_shutdown": ["bad"]},
        },
        tmp_path,
    )
    result = resolver.run_shutdown_tasks()
    assert not result.ok
    assert result.failures and result.failures[0].startswith("bad:")


def test_alias_listing_does_not_import_modules(tmp_path: Path) -> None:
    resolver = Resolver(
        {
            "paths": {"aliases": {"data": "data.json"}},
            "imports": {"later": "missing.module.function"},
            "modules": {"later": "missing.module"},
        },
        tmp_path,
    )
    assert resolver.aliases()["imports"] == ("later",)


@pytest.mark.parametrize("document", ["false", "[]", "0", "''"])
def test_rejects_falsey_non_mapping_yaml(tmp_path: Path, document: str) -> None:
    config = tmp_path / "bad.yaml"
    config.write_text(document, encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        Resolver.from_yaml(config)


@pytest.mark.parametrize("section", [None, [], "startup"])
def test_rejects_malformed_lifecycle_container(tmp_path: Path, section) -> None:
    resolver = Resolver({"background_tasks": section}, tmp_path)
    for action in (resolver.aliases, resolver.run_startup_tasks, resolver.run_shutdown_tasks):
        with pytest.raises(ValueError, match="background_tasks must be a mapping"):
            action()


def test_rejects_malformed_paths_container(tmp_path: Path) -> None:
    resolver = Resolver({"paths": []}, tmp_path)
    with pytest.raises(ValueError, match="paths.aliases"):
        resolver.aliases()
