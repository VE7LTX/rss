#!/usr/bin/env python3
"""Generate export files and indexes from feed registry."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
import xml.etree.ElementTree as ET

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal envs
    yaml = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from scripts.utils.simple_yaml import load_simple_yaml


def load_feed(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        if yaml is not None:
            return yaml.safe_load(handle)
        return load_simple_yaml(handle.read())


def sorted_feeds(feeds_dir: Path) -> List[Dict[str, Any]]:
    feeds = [load_feed(path) for path in feeds_dir.glob("*.yml")]
    return sorted(feeds, key=lambda item: item.get("id", ""))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, feeds: List[Dict[str, Any]]) -> None:
    fieldnames = [
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for feed in feeds:
            row = dict(feed)
            row["tags"] = ",".join(feed.get("tags", []))
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def write_opml(path: Path, feeds: List[Dict[str, Any]]) -> None:
    opml = ET.Element("opml", version="1.0")
    head = ET.SubElement(opml, "head")
    title = ET.SubElement(head, "title")
    title.text = "RSS Registry Feeds"
    body = ET.SubElement(opml, "body")

    for feed in feeds:
        outline = ET.SubElement(body, "outline")
        outline.set("text", feed.get("title", ""))
        outline.set("title", feed.get("title", ""))
        outline.set("type", "rss")
        outline.set("xmlUrl", feed.get("feed_url", ""))
        outline.set("htmlUrl", feed.get("site_url", ""))

    tree = ET.ElementTree(opml)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def build_indexes(feeds: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[str]]]:
    indexes = {
        "index-by-tag": {},
        "index-by-category": {},
        "index-by-region": {},
        "index-by-source-type": {},
    }

    for feed in feeds:
        feed_id = feed.get("id", "")
        for tag in feed.get("tags", []):
            indexes["index-by-tag"].setdefault(tag, []).append(feed_id)
        category = feed.get("category")
        if category:
            indexes["index-by-category"].setdefault(category, []).append(feed_id)
        region = feed.get("region")
        if region:
            indexes["index-by-region"].setdefault(region, []).append(feed_id)
        source_type = feed.get("source_type")
        if source_type:
            indexes["index-by-source-type"].setdefault(source_type, []).append(feed_id)

    for index in indexes.values():
        for key, items in index.items():
            index[key] = sorted(items)

    return indexes


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate feed exports and indexes.")
    parser.add_argument(
        "--feeds-dir",
        default="data/feeds",
        help="Directory containing feed YAML files.",
    )
    parser.add_argument(
        "--dist-dir",
        default="dist",
        help="Output directory for exports.",
    )
    args = parser.parse_args()

    feeds_dir = Path(args.feeds_dir)
    dist_dir = Path(args.dist_dir)
    indexes_dir = dist_dir / "indexes"
    dist_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)

    feeds = sorted_feeds(feeds_dir)

    write_json(dist_dir / "feeds.json", feeds)
    write_csv(dist_dir / "feeds.csv", feeds)
    write_opml(dist_dir / "feeds.opml", feeds)

    indexes = build_indexes(feeds)
    for name, payload in indexes.items():
        write_json(indexes_dir / f"{name}.json", payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
