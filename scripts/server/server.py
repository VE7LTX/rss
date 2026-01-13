"""
Live updates server for The RSS Encyclopedia.

Serves static assets from /public and /dist plus a simple API endpoint
for fetching live updates from selected feeds.
"""

from __future__ import annotations

import json
import os
import urllib.parse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
FEEDS_DIR = DATA_DIR / "feeds"
PUBLIC_DIR = ROOT / "public"
DIST_DIR = ROOT / "dist"
CACHE_DIR = ROOT / "cache"
CACHE_FILE = CACHE_DIR / "updates.json"
CACHE_TTL_SECONDS = 600
MAX_ITEMS_PER_FEED = 10
MAX_TOTAL_ITEMS = 30


class FeedFetchError(Exception):
    """Represents a feed fetch failure."""


def load_feed_index() -> Dict[str, Dict[str, Any]]:
    """Load feed metadata keyed by feed id from YAML files."""
    from scripts.lib.yamlish import load_yaml

    feeds: Dict[str, Dict[str, Any]] = {}
    for path in FEEDS_DIR.glob("*.yml"):
        data = load_yaml(path)
        if isinstance(data, dict) and data.get("id"):
            feeds[data["id"]] = data
    return feeds


def fetch_feed_xml(url: str, timeout: int = 12) -> str:
    """Fetch feed XML with a basic user agent."""
    request = Request(url, headers={"User-Agent": "rss-encyclopedia/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            content = response.read(200000)
            encoding = response.headers.get("Content-Encoding", "").lower()
            if "gzip" in encoding:
                import gzip

                content = gzip.decompress(content)
            return content.decode("utf-8", errors="ignore")
    except Exception as exc:
        raise FeedFetchError(str(exc))


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse common RSS/Atom date formats into datetime objects."""
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


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamps used in cache entries."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def parse_rss_items(xml_text: str) -> List[Dict[str, Any]]:
    """Parse RSS or RDF feed items into a normalized list."""
    items: List[Dict[str, Any]] = []
    root = ET.fromstring(xml_text)

    channel = root.find("channel")
    if channel is None:
        channel = root.find("{http://purl.org/rss/1.0/}channel")

    if channel is not None:
        for item in channel.findall("item"):
            items.append(extract_rss_item(item))
    else:
        for item in root.findall("{http://purl.org/rss/1.0/}item"):
            items.append(extract_rss_item(item))

    return items


def extract_rss_item(item: ET.Element) -> Dict[str, Any]:
    """Extract fields from an RSS item element."""
    title = (item.findtext("title") or "").strip()
    link = (item.findtext("link") or "").strip()
    pub_date = (
        item.findtext("pubDate")
        or item.findtext("{http://purl.org/dc/elements/1.1/}date")
        or item.findtext("dc:date")
        or ""
    ).strip()
    return {
        "title": title,
        "url": link,
        "published": pub_date,
    }


def parse_atom_items(xml_text: str) -> List[Dict[str, Any]]:
    """Parse Atom feed entries into a normalized list."""
    items: List[Dict[str, Any]] = []
    root = ET.fromstring(xml_text)
    ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.findall(f"{ns}entry"):
        title = (entry.findtext(f"{ns}title") or "").strip()
        updated = (entry.findtext(f"{ns}updated") or entry.findtext(f"{ns}published") or "").strip()
        link = ""
        link_el = entry.find(f"{ns}link")
        if link_el is not None:
            link = (link_el.attrib.get("href") or "").strip()
        items.append({"title": title, "url": link, "published": updated})
    return items


def parse_items(xml_text: str) -> List[Dict[str, Any]]:
    """Parse feed XML into items, auto-detecting RSS/Atom."""
    try:
        if "<feed" in xml_text.lower():
            return parse_atom_items(xml_text)
        return parse_rss_items(xml_text)
    except ET.ParseError:
        return []

def load_cache() -> Dict[str, Any]:
    """Load cached feed items from disk."""
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_cache(cache: Dict[str, Any]) -> None:
    """Persist cached feed items to disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


CACHE = load_cache()


def normalize_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize parsed items and keep only supported fields."""
    normalized: List[Dict[str, Any]] = []
    for item in items:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        published_raw = (item.get("published") or "").strip()
        published_dt = parse_datetime(published_raw)
        published = (
            published_dt.isoformat().replace("+00:00", "Z") if published_dt else published_raw
        )
        if not title and not url:
            continue
        normalized.append({"title": title, "url": url, "published": published})
    return normalized


def build_updates(
    feed_ids: List[str],
    limit: int = MAX_TOTAL_ITEMS,
    force: bool = False,
) -> Dict[str, Any]:
    """Fetch updates for selected feeds and return merged updates and feed metadata."""
    feed_index = load_feed_index()
    updates: List[Dict[str, Any]] = []
    feed_meta: Dict[str, Dict[str, Any]] = {}
    now = datetime.now(tz=timezone.utc)

    for feed_id in feed_ids:
        feed = feed_index.get(feed_id)
        if not feed:
            continue

        cached = CACHE.get(feed_id)
        cached_items: List[Dict[str, Any]] = []
        cached_fetched_at: Optional[datetime] = None
        if cached:
            cached_items = cached.get("items", [])
            cached_fetched_at = parse_iso_datetime(cached.get("fetched_at"))

        use_cache = False
        if cached_items and cached_fetched_at and not force:
            age = (now - cached_fetched_at).total_seconds()
            if age < CACHE_TTL_SECONDS:
                use_cache = True

        if use_cache:
            items = cached_items
            fetched_at = cached.get("fetched_at")
        else:
            try:
                xml_text = fetch_feed_xml(feed["feed_url"])
                parsed_items = parse_items(xml_text)
                items = normalize_items(parsed_items)[:MAX_ITEMS_PER_FEED]
                fetched_at = now.isoformat().replace("+00:00", "Z")
                CACHE[feed_id] = {"fetched_at": fetched_at, "items": items}
            except FeedFetchError:
                items = cached_items
                fetched_at = cached.get("fetched_at") if cached else None

        last_published = ""
        for item in items:
            published_dt = parse_datetime(item.get("published"))
            if published_dt:
                last_published = published_dt.isoformat().replace("+00:00", "Z")
                break

        feed_meta[feed_id] = {
            "last_published": last_published,
            "last_fetched": fetched_at or "",
            "item_count": len(items),
        }

        for item in items:
            updates.append(
                {
                    "feed_id": feed_id,
                    "feed_title": feed.get("title"),
                    "title": item.get("title"),
                    "url": item.get("url") or feed.get("site_url"),
                    "published": item.get("published") or "",
                }
            )

    save_cache(CACHE)

    updates.sort(
        key=lambda item: parse_datetime(item.get("published") or "") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return {"updates": updates[:limit], "feeds": feed_meta}


class RegistryHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves static files and the updates API."""

    def do_GET(self) -> None:  # noqa: N802 - required by base class
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/updates":
            self.handle_updates(parsed)
            return

        super().do_GET()

    def handle_updates(self, parsed: urllib.parse.ParseResult) -> None:
        """Return JSON feed updates for selected feeds."""
        params = urllib.parse.parse_qs(parsed.query)
        feed_ids = [item for item in params.get("ids", [""])[0].split(",") if item]
        limit = int(params.get("limit", ["30"])[0])
        force = params.get("force", ["0"])[0] == "1"

        payload_data = build_updates(feed_ids, limit=limit, force=force)
        payload = json.dumps(payload_data, indent=2)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload.encode("utf-8"))


def main() -> None:
    """Run the local server."""
    os.chdir(ROOT)
    handler = RegistryHandler
    server = ThreadingHTTPServer(("127.0.0.1", 8000), handler)
    print("Serving The RSS Encyclopedia on http://127.0.0.1:8000/public/index.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
