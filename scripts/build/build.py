import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.lib.yamlish import load_yaml
DATA_DIR = ROOT / "data"
FEEDS_DIR = DATA_DIR / "feeds"
DIST_DIR = ROOT / "dist"
INDEX_DIR = DIST_DIR / "indexes"


def load_data():
    categories = load_yaml(DATA_DIR / "categories.yml").get("categories", [])
    tags = load_yaml(DATA_DIR / "tags.yml").get("tags", [])
    locales = load_yaml(DATA_DIR / "locales.yml")

    feeds = []
    for feed_path in sorted(FEEDS_DIR.glob("*.yml")):
        feeds.append(load_yaml(feed_path))

    return {
        "categories": categories,
        "tags": tags,
        "languages": locales.get("languages", []),
        "regions": locales.get("regions", []),
        "feeds": feeds,
    }


def ensure_dirs():
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def build_indexes(feeds):
    indexes = {
        "tag": {},
        "category": {},
        "region": {},
        "source_type": {},
    }

    for feed in feeds:
        feed_id = feed.get("id")
        if not feed_id:
            continue

        indexes["category"].setdefault(feed.get("category"), []).append(feed_id)
        indexes["region"].setdefault(feed.get("region"), []).append(feed_id)
        indexes["source_type"].setdefault(feed.get("source_type"), []).append(feed_id)

        for tag in feed.get("tags", []):
            indexes["tag"].setdefault(tag, []).append(feed_id)

    return indexes


def enrich_feeds(data):
    category_lookup = {item["id"]: item for item in data["categories"]}
    tag_lookup = {item["id"]: item for item in data["tags"]}
    language_lookup = {item["code"]: item for item in data["languages"]}
    region_lookup = {item["code"]: item for item in data["regions"]}

    enriched = []
    for feed in data["feeds"]:
        entry = dict(feed)
        entry["category_title"] = category_lookup.get(feed.get("category"), {}).get("title")
        entry["tag_titles"] = [tag_lookup.get(tag, {}).get("title") for tag in feed.get("tags", [])]
        entry["language_name"] = language_lookup.get(feed.get("language"), {}).get("name")
        entry["region_name"] = region_lookup.get(feed.get("region"), {}).get("name")
        enriched.append(entry)

    return enriched


def build_json(data, feeds):
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "categories": data["categories"],
        "tags": data["tags"],
        "languages": data["languages"],
        "regions": data["regions"],
        "feeds": feeds,
    }

    (DIST_DIR / "feeds.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build_csv(feeds):
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
    with open(DIST_DIR / "feeds.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for feed in feeds:
            row = {key: feed.get(key) for key in fieldnames}
            row["tags"] = "|".join(feed.get("tags", []))
            writer.writerow(row)


def build_opml(feeds):
    outlines = []
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

    (DIST_DIR / "feeds.opml").write_text(opml, encoding="utf-8")


def escape_xml(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_indexes_files(indexes):
    (INDEX_DIR / "index-by-tag.json").write_text(json.dumps(indexes["tag"], indent=2), encoding="utf-8")
    (INDEX_DIR / "index-by-category.json").write_text(
        json.dumps(indexes["category"], indent=2), encoding="utf-8"
    )
    (INDEX_DIR / "index-by-region.json").write_text(
        json.dumps(indexes["region"], indent=2), encoding="utf-8"
    )
    (INDEX_DIR / "index-by-source-type.json").write_text(
        json.dumps(indexes["source_type"], indent=2), encoding="utf-8"
    )


def build_items(feeds):
    items = []
    now = datetime.utcnow()
    for feed in feeds:
        for idx in range(2):
            published = now - timedelta(hours=(idx * 6))
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
    (DIST_DIR / "items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")


def main():
    ensure_dirs()
    data = load_data()
    feeds = enrich_feeds(data)
    indexes = build_indexes(feeds)

    build_json(data, feeds)
    build_csv(feeds)
    build_opml(feeds)
    build_indexes_files(indexes)
    build_items(feeds)

    print(f"Built {len(feeds)} feeds into {DIST_DIR}")


if __name__ == "__main__":
    main()
