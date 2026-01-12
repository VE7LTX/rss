import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.lib.yamlish import load_yaml
DATA_DIR = ROOT / "data"
FEEDS_DIR = DATA_DIR / "feeds"

REQUIRED_FIELDS = {
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
}

ALLOWED_FORMATS = {"rss", "atom", "json"}
ALLOWED_SOURCE_TYPES = {
    "publisher",
    "independent",
    "academic",
    "ngo",
    "government",
    "think-tank",
    "community",
    "corporate",
    "personal",
}
ALLOWED_STATUS = {"active", "inactive", "moved", "dead"}


def load_vocab():
    categories = load_yaml(DATA_DIR / "categories.yml").get("categories", [])
    tags = load_yaml(DATA_DIR / "tags.yml").get("tags", [])
    locales = load_yaml(DATA_DIR / "locales.yml")

    return {
        "categories": {item["id"] for item in categories},
        "tags": {item["id"] for item in tags},
        "languages": {item["code"] for item in locales.get("languages", [])},
        "regions": {item["code"] for item in locales.get("regions", [])},
    }


def validate_feed(feed_path, vocab, seen_ids):
    errors = []
    warnings = []
    feed = load_yaml(feed_path)

    missing = REQUIRED_FIELDS - set(feed.keys())
    if missing:
        errors.append(f"missing_fields: {sorted(missing)}")

    feed_id = feed.get("id")
    if feed_id:
        if feed_id in seen_ids:
            errors.append("duplicate_id")
        seen_ids.add(feed_id)
        if feed_path.stem != feed_id:
            errors.append(f"filename_mismatch: expected {feed_id}.yml")

    category = feed.get("category")
    if category and category not in vocab["categories"]:
        errors.append(f"unknown_category: {category}")

    tags = feed.get("tags") or []
    if not isinstance(tags, list):
        errors.append("tags_not_list")
    else:
        unknown_tags = [tag for tag in tags if tag not in vocab["tags"]]
        if unknown_tags:
            errors.append(f"unknown_tags: {unknown_tags}")

    language = feed.get("language")
    if language and language not in vocab["languages"]:
        errors.append(f"unknown_language: {language}")

    region = feed.get("region")
    if region and region not in vocab["regions"]:
        errors.append(f"unknown_region: {region}")

    fmt = feed.get("format")
    if fmt and fmt not in ALLOWED_FORMATS:
        errors.append(f"invalid_format: {fmt}")

    source_type = feed.get("source_type")
    if source_type and source_type not in ALLOWED_SOURCE_TYPES:
        errors.append(f"invalid_source_type: {source_type}")

    status = feed.get("status")
    if status and status not in ALLOWED_STATUS:
        errors.append(f"invalid_status: {status}")

    if not feed.get("tags"):
        warnings.append("empty_tags")

    return {
        "feed": feed_path.name,
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate RSS registry data.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--out", type=str, help="Write JSON report to a file.")
    args = parser.parse_args()

    vocab = load_vocab()
    seen_ids = set()

    results = []
    error_count = 0
    warning_count = 0

    for feed_path in sorted(FEEDS_DIR.glob("*.yml")):
        result = validate_feed(feed_path, vocab, seen_ids)
        results.append(result)
        error_count += len(result["errors"])
        warning_count += len(result["warnings"])

    report = {
        "feeds_checked": len(results),
        "errors": error_count,
        "warnings": warning_count,
        "results": results,
    }

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Feeds checked: {report['feeds_checked']}")
        print(f"Errors: {report['errors']} | Warnings: {report['warnings']}")
        for entry in results:
            if entry["errors"] or entry["warnings"]:
                print(f"- {entry['feed']}")
                for err in entry["errors"]:
                    print(f"  ERROR: {err}")
                for warn in entry["warnings"]:
                    print(f"  WARN: {warn}")

    raise SystemExit(1 if error_count else 0)


if __name__ == "__main__":
    main()
