"""
Registry build CLI.

Generates deterministic outputs (JSON, CSV, OPML, indexes, demo items)
from the curated feed registry.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.lib.yamlish import load_yaml

FeedRecord = Dict[str, Any]


@dataclass
class BuildPaths:
    """Container for all build-related paths."""

    root: Path
    data_dir: Path
    feeds_dir: Path
    dist_dir: Path
    index_dir: Path


@dataclass
class BuildSummary:
    """High-level build output summary."""

    feed_count: int
    dist_dir: Path


def build_paths(root: Path) -> BuildPaths:
    """Derive repository paths from the root directory."""
    data_dir = root / "data"
    feeds_dir = data_dir / "feeds"
    dist_dir = root / "dist"
    index_dir = dist_dir / "indexes"
    return BuildPaths(root, data_dir, feeds_dir, dist_dir, index_dir)


def load_data(paths: BuildPaths) -> Dict[str, Any]:
    """Load vocabularies and feed entries from the data directory."""
    categories = load_yaml(paths.data_dir / "categories.yml").get("categories", [])
    tags = load_yaml(paths.data_dir / "tags.yml").get("tags", [])
    locales = load_yaml(paths.data_dir / "locales.yml")

    feeds: List[FeedRecord] = []
    for feed_path in sorted(paths.feeds_dir.glob("*.yml")):
        feeds.append(load_yaml(feed_path))

    return {
        "categories": categories,
        "tags": tags,
        "languages": locales.get("languages", []),
        "regions": locales.get("regions", []),
        "feeds": feeds,
    }


def ensure_dirs(paths: BuildPaths) -> None:
    """Create output directories if they do not exist."""
    paths.dist_dir.mkdir(parents=True, exist_ok=True)
    paths.index_dir.mkdir(parents=True, exist_ok=True)


def build_indexes(feeds: List[FeedRecord]) -> Dict[str, Dict[str, List[str]]]:
    """Build indexes for faster filtering by tag, category, region, and source type."""
    indexes: Dict[str, Dict[str, List[str]]] = {
        "tag": {},
        "category": {},
        "region": {},
        "source_type": {},
    }

    for feed in feeds:
        feed_id = feed.get("id")
        if not feed_id:
            continue

        category = feed.get("category")
        if category:
            indexes["category"].setdefault(category, []).append(feed_id)

        region = feed.get("region")
        if region:
            indexes["region"].setdefault(region, []).append(feed_id)

        source_type = feed.get("source_type")
        if source_type:
            indexes["source_type"].setdefault(source_type, []).append(feed_id)

        for tag in feed.get("tags", []) or []:
            indexes["tag"].setdefault(tag, []).append(feed_id)

    return indexes


def enrich_feeds(data: Dict[str, Any]) -> List[FeedRecord]:
    """Attach human-readable titles to each feed record."""
    category_lookup = {item["id"]: item for item in data["categories"]}
    tag_lookup = {item["id"]: item for item in data["tags"]}
    language_lookup = {item["code"]: item for item in data["languages"]}
    region_lookup = {item["code"]: item for item in data["regions"]}

    enriched: List[FeedRecord] = []
    for feed in data["feeds"]:
        entry = dict(feed)
        entry["category_title"] = category_lookup.get(feed.get("category"), {}).get("title")
        entry["tag_titles"] = [tag_lookup.get(tag, {}).get("title") for tag in feed.get("tags", [])]
        entry["language_name"] = language_lookup.get(feed.get("language"), {}).get("name")
        entry["region_name"] = region_lookup.get(feed.get("region"), {}).get("name")
        enriched.append(entry)

    return enriched


def build_json(paths: BuildPaths, data: Dict[str, Any], feeds: List[FeedRecord]) -> None:
    """Write the JSON registry output."""
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "categories": data["categories"],
        "tags": data["tags"],
        "languages": data["languages"],
        "regions": data["regions"],
        "feeds": feeds,
    }

    (paths.dist_dir / "feeds.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_csv(paths: BuildPaths, feeds: List[FeedRecord]) -> None:
    """Write the CSV registry output."""
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

    with open(paths.dist_dir / "feeds.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for feed in feeds:
            row = {key: feed.get(key) for key in fieldnames}
            row["tags"] = "|".join(feed.get("tags", []) or [])
            writer.writerow(row)


def build_opml(paths: BuildPaths, feeds: List[FeedRecord]) -> None:
    """Write the OPML output for traditional feed readers."""
    outlines: List[str] = []
    for feed in feeds:
        outlines.append(
            "    <outline text=\"{title}\" title=\"{title}\" type=\"rss\" xmlUrl=\"{feed_url}\" htmlUrl=\"{site_url}\" category=\"{category}\" />".format(
                title=escape_xml(feed.get("title", "")),
                feed_url=escape_xml(feed.get("feed_url", "")),
                site_url=escape_xml(feed.get("site_url", "")),
                category=escape_xml(feed.get("category", "")),
            )
        )

    opml = "\n".join(
        [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<opml version=\"1.0\">",
            "  <head>",
            "    <title>RSS Registry</title>",
            "  </head>",
            "  <body>",
            *outlines,
            "  </body>",
            "</opml>",
            "",
        ]
    )

    (paths.dist_dir / "feeds.opml").write_text(opml, encoding="utf-8")


def escape_xml(text: Any) -> str:
    """Escape XML-special characters for OPML output."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_indexes_files(paths: BuildPaths, indexes: Dict[str, Dict[str, List[str]]]) -> None:
    """Write index files used by the prototype UI."""
    (paths.index_dir / "index-by-tag.json").write_text(
        json.dumps(indexes["tag"], indent=2), encoding="utf-8"
    )
    (paths.index_dir / "index-by-category.json").write_text(
        json.dumps(indexes["category"], indent=2), encoding="utf-8"
    )
    (paths.index_dir / "index-by-region.json").write_text(
        json.dumps(indexes["region"], indent=2), encoding="utf-8"
    )
    (paths.index_dir / "index-by-source-type.json").write_text(
        json.dumps(indexes["source_type"], indent=2), encoding="utf-8"
    )


def build_items(paths: BuildPaths, feeds: List[FeedRecord], now: datetime | None = None) -> None:
    """Generate demo update items for the prototype UI."""
    items: List[Dict[str, Any]] = []
    timestamp = now or datetime.utcnow()

    for feed in feeds:
        for idx in range(2):
            published = timestamp - timedelta(hours=(idx * 6))
            items.append(
                {
                    "feed_id": feed.get("id"),
                    "feed_title": feed.get("title"),
                    "title": f"{feed.get('title')} sample update {idx + 1}",
                    "url": feed.get("site_url"),
                    "published": published.isoformat() + "Z",
                    "summary": "Demo item generated for the prototype feed viewer.",
                }
            )

    items.sort(key=lambda item: item["published"], reverse=True)
    (paths.dist_dir / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")


def build_all(root: Path) -> BuildSummary:
    """Run the full build pipeline and return a summary."""
    paths = build_paths(root)
    ensure_dirs(paths)
    data = load_data(paths)
    feeds = enrich_feeds(data)
    indexes = build_indexes(feeds)

    build_json(paths, data, feeds)
    build_csv(paths, feeds)
    build_opml(paths, feeds)
    build_indexes_files(paths, indexes)
    build_items(paths, feeds)

    return BuildSummary(feed_count=len(feeds), dist_dir=paths.dist_dir)


def main() -> None:
    """CLI entry point."""
    summary = build_all(ROOT)
    print(f"Built {summary.feed_count} feeds into {summary.dist_dir}")


if __name__ == "__main__":
    main()
