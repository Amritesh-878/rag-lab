"""Keep repos.toml, the README tables and .gitmodules naming the same repos."""

from __future__ import annotations

import configparser
import re
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SELF_NAME = "rag-lab"
URL_PREFIX = "https://github.com/Amritesh-878/"
REPO_NAME = re.compile(r"\brag-[a-z]+\b")
SUBMODULE_SECTION = re.compile(r'^submodule "(?P<path>[^"]+)"$')


def load_map() -> list[dict[str, Any]]:
    with (ROOT / "repos.toml").open("rb") as handle:
        entries: list[dict[str, Any]] = tomllib.load(handle)["repo"]
    return entries


def mapped_names() -> set[str]:
    return {entry["name"] for entry in load_map()}


def finished_names() -> set[str]:
    return {entry["name"] for entry in load_map() if not entry.get("in_progress", False)}


def readme_text() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def names_in(text: str) -> set[str]:
    return set(REPO_NAME.findall(text)) - {SELF_NAME}


def table_names() -> set[str]:
    rows = [line for line in readme_text().splitlines() if line.lstrip().startswith("|")]
    return names_in("\n".join(rows))


def load_submodules() -> dict[str, dict[str, str]]:
    parser = configparser.ConfigParser()
    parser.read(ROOT / ".gitmodules", encoding="utf-8")
    found: dict[str, dict[str, str]] = {}
    for section in parser.sections():
        match = SUBMODULE_SECTION.match(section)
        assert match, f"unexpected .gitmodules section: {section}"
        path = parser[section]["path"]
        found[Path(path).name] = {"path": path, "url": parser[section]["url"]}
    return found


def test_every_mapped_repo_is_in_a_readme_table() -> None:
    missing = mapped_names() - table_names()
    assert not missing, f"in repos.toml but in no README table: {sorted(missing)}"


def test_readme_names_no_unmapped_repo() -> None:
    extra = names_in(readme_text()) - mapped_names()
    assert not extra, f"named in the README but not in repos.toml: {sorted(extra)}"


def test_submodules_are_the_finished_repos() -> None:
    submodules = load_submodules()
    assert set(submodules) == finished_names(), (
        f"only in .gitmodules: {sorted(set(submodules) - finished_names())}, "
        f"missing from .gitmodules: {sorted(finished_names() - set(submodules))}"
    )


def test_submodules_point_at_the_mapped_urls() -> None:
    urls = {entry["name"]: entry["url"] for entry in load_map()}
    for name, submodule in load_submodules().items():
        assert submodule["path"] in {name, f"repos/{name}"}
        assert submodule["url"] == f"{urls[name]}.git"


def test_map_entries_are_complete() -> None:
    entries = load_map()
    assert len(entries) == len(mapped_names()), "a repo is listed twice in repos.toml"
    for entry in entries:
        assert entry["url"] == URL_PREFIX + entry["name"]
        assert entry["role"] in {"base", "architecture", "benchmark"}
        if not entry.get("in_progress", False):
            assert re.fullmatch(r"v\d+\.\d+\.\d+", entry["rag_core_tag"]), entry["name"]
