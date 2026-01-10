#!/usr/bin/env python3
"""Validate feed records against the required schema fields."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    yaml = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from scripts.utils.simple_yaml import load_simple_yaml

REQUIRED_FIELDS = [
    "id",
    "title",
    "site_url",
    "feed_url",
    "format",
    "category",
    "tags",
    "language",
    "region",
    "source_type",
    "status",
    "added",
]


def load_feed(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        if yaml is not None:
            return yaml.safe_load(handle)
        return load_simple_yaml(handle.read())


def validate_feed(path: Path) -> Dict[str, Any]:
    errors: List[str] = []
    feed = load_feed(path) or {}

    if not isinstance(feed, dict):
        return {"file": str(path), "errors": ["Feed entry must be a mapping."]}

    for field in REQUIRED_FIELDS:
        if field not in feed:
            errors.append(f"Missing required field: {field}")

    if "tags" in feed and not isinstance(feed["tags"], list):
        errors.append("Field 'tags' must be a list.")

    return {"file": str(path), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RSS feed records.")
    parser.add_argument(
        "--feeds-dir",
        default="data/feeds",
        help="Directory containing feed YAML files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON report.",
    )
    args = parser.parse_args()

    feeds_dir = Path(args.feeds_dir)
    results = [validate_feed(path) for path in sorted(feeds_dir.glob("*.yml"))]

    failed = [result for result in results if result["errors"]]

    if args.json:
        print(json.dumps({"results": results}, indent=2))
    else:
        for result in failed:
            print(f"{result['file']}")
            for error in result["errors"]:
                print(f"  - {error}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
