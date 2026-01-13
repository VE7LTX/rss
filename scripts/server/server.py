"""
Live updates server for The RSS Encyclopedia.

Serves static assets from /public and /dist plus a simple API endpoint
for fetching live updates from selected feeds.
"""

from __future__ import annotations

import json
import os
import urllib.parse
from datetime import datetime
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
            content = response.read(60000)
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
        return parsedate_to_datetime(value)
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


def build_updates(feed_ids: List[str], limit: int = 30) -> List[Dict[str, Any]]:
    """Fetch updates for selected feeds and return a merged list."""
    feed_index = load_feed_index()
    updates: List[Dict[str, Any]] = []

    for feed_id in feed_ids:
        feed = feed_index.get(feed_id)
        if not feed:
            continue
        try:
            xml_text = fetch_feed_xml(feed["feed_url"])
            items = parse_items(xml_text)
        except FeedFetchError:
            continue

        for item in items[:10]:
            published_dt = parse_datetime(item.get("published"))
            updates.append(
                {
                    "feed_id": feed_id,
                    "feed_title": feed.get("title"),
                    "title": item.get("title"),
                    "url": item.get("url") or feed.get("site_url"),
                    "published": (
                        published_dt.isoformat() + "Z" if published_dt else item.get("published") or ""
                    ),
                }
            )

    updates.sort(key=lambda item: item.get("published", ""), reverse=True)
    return updates[:limit]


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

        updates = build_updates(feed_ids, limit=limit)
        payload = json.dumps({"updates": updates}, indent=2)

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
