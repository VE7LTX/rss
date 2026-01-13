"""
Registry validation CLI.

Validates feed records against the schema requirements and controlled
vocabularies, emitting a console summary or JSON report.
"""

from __future__ import annotations

import argparse
import json
import sys
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.lib.yamlish import load_yaml

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


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse RSS/Atom timestamps into UTC datetimes."""
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except Exception:
            return None


def fetch_feed_xml(url: str, timeout: int = 10) -> str:
    """Fetch feed XML content from the network."""
    request = Request(url, headers={"User-Agent": "rss-encyclopedia-validator/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content = response.read(250000)
        encoding = response.headers.get("Content-Encoding", "").lower()
        if "gzip" in encoding:
            import gzip

            content = gzip.decompress(content)
        return content.decode("utf-8", errors="ignore")


def parse_feed_items(xml_text: str) -> List[Dict[str, str]]:
    """Parse RSS/Atom entries into a list of items with published timestamps."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    items: List[Dict[str, str]] = []
    if root.tag.endswith("feed") or "<feed" in xml_text.lower():
        ns = "{http://www.w3.org/2005/Atom}"
        entries = root.findall(f"{ns}entry") or root.findall("entry")
        for entry in entries:
            published = entry.findtext(f"{ns}updated") or entry.findtext(f"{ns}published") or ""
            if not published:
                published = entry.findtext("updated") or entry.findtext("published") or ""
            items.append({"published": published.strip()})
        return items

    channel = root.find("channel")
    if channel is None:
        channel = root.find("{http://purl.org/rss/1.0/}channel")

    if channel is not None:
        candidates = channel.findall("item")
        if not candidates:
            candidates = channel.findall(".//item")
    else:
        candidates = root.findall("{http://purl.org/rss/1.0/}item") or root.findall(".//item")

    for item in candidates:
        published = (
            item.findtext("pubDate")
            or item.findtext("{http://purl.org/dc/elements/1.1/}date")
            or item.findtext("dc:date")
            or ""
        )
        items.append({"published": published.strip()})

    return items


def fallback_item_count(xml_text: str) -> int:
    """Estimate item count when XML parsing fails."""
    return len(re.findall(r"<item\b", xml_text, re.IGNORECASE)) + len(
        re.findall(r"<entry\b", xml_text, re.IGNORECASE)
    )


def fallback_dates(xml_text: str) -> List[str]:
    """Extract date strings from XML tags via regex as a fallback."""
    patterns = ["pubDate", "updated", "published", "dc:date"]
    results: List[str] = []
    for tag in patterns:
        results.extend(re.findall(rf"<{tag}>(.*?)</{tag}>", xml_text, re.IGNORECASE | re.DOTALL))
    return [value.strip() for value in results if value.strip()]


def run_health_check(url: str, timeout: int = 10) -> HealthResult:
    """Check feed availability and last-published timestamp."""
    try:
        xml_text = fetch_feed_xml(url, timeout=timeout)
        items = parse_feed_items(xml_text)
        published_dates = [parse_datetime(item.get("published")) for item in items]
        published_dates = [dt for dt in published_dates if dt]
        last_published = ""
        if published_dates:
            last_published = max(published_dates).isoformat().replace("+00:00", "Z")
        ok = bool(items)
        error = None if ok else "no items parsed"
        item_count = len(items)

        if not ok:
            fallback = fallback_dates(xml_text)
            fallback_dates_parsed = [parse_datetime(value) for value in fallback]
            fallback_dates_parsed = [dt for dt in fallback_dates_parsed if dt]
            if fallback_dates_parsed:
                last_published = max(fallback_dates_parsed).isoformat().replace("+00:00", "Z")
            item_count = fallback_item_count(xml_text)
            ok = item_count > 0
            error = None if ok else "no items parsed"

        return HealthResult(
            ok=ok,
            status=200,
            error=error,
            item_count=item_count,
            last_published=last_published,
        )
    except Exception as exc:
        return HealthResult(
            ok=False,
            status=None,
            error=str(exc),
            item_count=0,
            last_published="",
        )

@dataclass
class FeedResult:
    """Stores validation findings for a single feed file."""

    feed: str
    errors: List[str]
    warnings: List[str]
    health: Optional["HealthResult"] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the result for JSON output."""
        payload = {
            "feed": self.feed,
            "errors": self.errors,
            "warnings": self.warnings,
        }
        if self.health is not None:
            payload["health"] = self.health.to_dict()
        return payload


@dataclass
class HealthResult:
    """Stores health-check data for a feed URL."""

    ok: bool
    status: Optional[int]
    error: Optional[str]
    item_count: int
    last_published: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize health results to JSON."""
        return {
            "ok": self.ok,
            "status": self.status,
            "error": self.error,
            "item_count": self.item_count,
            "last_published": self.last_published,
        }


@dataclass
class ValidationReport:
    """Aggregated validation results across all feeds."""

    feeds_checked: int
    errors: int
    warnings: int
    results: List[FeedResult]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the report for JSON output."""
        return {
            "feeds_checked": self.feeds_checked,
            "errors": self.errors,
            "warnings": self.warnings,
            "results": [result.to_dict() for result in self.results],
        }


def load_vocab(data_dir: Path) -> Dict[str, Set[str]]:
    """Load controlled vocabularies from the data directory."""
    categories = load_yaml(data_dir / "categories.yml").get("categories", [])
    tags = load_yaml(data_dir / "tags.yml").get("tags", [])
    locales = load_yaml(data_dir / "locales.yml")

    return {
        "categories": {item["id"] for item in categories},
        "tags": {item["id"] for item in tags},
        "languages": {item["code"] for item in locales.get("languages", [])},
        "regions": {item["code"] for item in locales.get("regions", [])},
    }


def validate_feed(
    feed_path: Path,
    vocab: Dict[str, Set[str]],
    seen_ids: Set[str],
    health_check: bool = False,
    health_timeout: int = 10,
) -> FeedResult:
    """Validate a single feed YAML file and return errors/warnings."""
    errors: List[str] = []
    warnings: List[str] = []

    feed = load_yaml(feed_path)
    if not isinstance(feed, dict):
        return FeedResult(feed=feed_path.name, errors=["invalid_yaml_root"], warnings=[])

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

    tags_value = feed.get("tags") or []
    if not isinstance(tags_value, list):
        errors.append("tags_not_list")
    else:
        unknown_tags = [tag for tag in tags_value if tag not in vocab["tags"]]
        if unknown_tags:
            errors.append(f"unknown_tags: {unknown_tags}")
        if not tags_value:
            warnings.append("empty_tags")

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

    health = None
    if health_check and feed.get("feed_url"):
        health = run_health_check(feed.get("feed_url"), timeout=health_timeout)

    return FeedResult(feed=feed_path.name, errors=errors, warnings=warnings, health=health)


def validate_all(
    feeds_dir: Path,
    vocab: Dict[str, Set[str]],
    health_check: bool = False,
    health_timeout: int = 10,
    offset: int = 0,
    limit: Optional[int] = None,
) -> ValidationReport:
    """Validate all feed files in a directory."""
    results: List[FeedResult] = []
    seen_ids: Set[str] = set()

    feed_paths = sorted(feeds_dir.glob("*.yml"))
    if offset:
        feed_paths = feed_paths[offset:]
    if limit is not None:
        feed_paths = feed_paths[:limit]

    for feed_path in feed_paths:
        results.append(
            validate_feed(
                feed_path,
                vocab,
                seen_ids,
                health_check=health_check,
                health_timeout=health_timeout,
            )
        )

    error_count = sum(len(result.errors) for result in results)
    warning_count = sum(len(result.warnings) for result in results)

    return ValidationReport(
        feeds_checked=len(results),
        errors=error_count,
        warnings=warning_count,
        results=results,
    )


def write_report(path: Path, report: ValidationReport) -> None:
    """Write a JSON validation report to disk."""
    path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def print_report(report: ValidationReport) -> None:
    """Print a human-readable validation summary."""
    print(f"Feeds checked: {report.feeds_checked}")
    print(f"Errors: {report.errors} | Warnings: {report.warnings}")
    for entry in report.results:
        if entry.errors or entry.warnings or (entry.health and not entry.health.ok):
            print(f"- {entry.feed}")
            for err in entry.errors:
                print(f"  ERROR: {err}")
            for warn in entry.warnings:
                print(f"  WARN: {warn}")
            if entry.health and not entry.health.ok:
                print(f"  HEALTH: {entry.health.error}")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the validation script."""
    parser = argparse.ArgumentParser(description="Validate RSS registry data.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--out", type=str, help="Write JSON report to a file.")
    parser.add_argument("--health", action="store_true", help="Run live feed health checks.")
    parser.add_argument(
        "--health-timeout",
        type=int,
        default=10,
        help="Timeout per feed request (seconds).",
    )
    parser.add_argument("--offset", type=int, default=0, help="Start index for batch validation.")
    parser.add_argument("--limit", type=int, help="Limit feeds for batch validation.")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()

    data_dir = ROOT / "data"
    feeds_dir = data_dir / "feeds"

    vocab = load_vocab(data_dir)
    report = validate_all(
        feeds_dir,
        vocab,
        health_check=args.health,
        health_timeout=args.health_timeout,
        offset=args.offset,
        limit=args.limit,
    )

    if args.out:
        write_report(Path(args.out), report)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print_report(report)

    raise SystemExit(1 if report.errors else 0)


if __name__ == "__main__":
    main()
