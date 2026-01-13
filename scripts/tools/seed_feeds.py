"""
Seed feed entries for the RSS Encyclopedia.

Usage:
  python scripts/tools/seed_feeds.py --verify
  python scripts/tools/seed_feeds.py --verify --write

The script verifies each feed URL with a GET request and writes YAML files
for entries that pass basic RSS/Atom detection.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.lib.yamlish import load_yaml


@dataclass
class FeedEntry:
    """Represents a feed entry to be written into data/feeds/."""

    id: str
    title: str
    site_url: str
    feed_url: str
    format: str
    category: str
    tags: List[str]
    language: str
    region: str
    source_type: str
    status: str
    added: str

    def to_yaml(self) -> str:
        """Serialize the entry into a YAML string."""
        lines = [
            f"id: {self.id}",
            f"title: {self.title}",
            f"site_url: {self.site_url}",
            f"feed_url: {self.feed_url}",
            f"format: {self.format}",
            f"category: {self.category}",
            "tags:",
            *[f"  - {tag}" for tag in self.tags],
            f"language: {self.language}",
            f"region: {self.region}",
            f"source_type: {self.source_type}",
            f"status: {self.status}",
            f"added: \"{self.added}\"",
        ]
        return "\n".join(lines) + "\n"


def load_vocab_ids() -> Dict[str, List[str]]:
    """Load vocabularies to validate tags/categories."""
    data_dir = ROOT / "data"
    categories = load_yaml(data_dir / "categories.yml").get("categories", [])
    tags = load_yaml(data_dir / "tags.yml").get("tags", [])
    locales = load_yaml(data_dir / "locales.yml")

    return {
        "categories": [item["id"] for item in categories],
        "tags": [item["id"] for item in tags],
        "languages": [item["code"] for item in locales.get("languages", [])],
        "regions": [item["code"] for item in locales.get("regions", [])],
    }


def feed_entries() -> List[FeedEntry]:
    """Return the curated list of new feed entries to seed."""
    today = dt.date.today().isoformat()
    entries = [
        # Global and regional news
        FeedEntry(
            id="al-jazeera-all",
            title="Al Jazeera - All News",
            site_url="https://www.aljazeera.com/",
            feed_url="https://www.aljazeera.com/xml/rss/all.xml",
            format="rss",
            category="news_current_affairs",
            tags=["global", "breaking"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="cnn-world",
            title="CNN - World",
            site_url="https://www.cnn.com/world",
            feed_url="http://rss.cnn.com/rss/edition_world.rss",
            format="rss",
            category="news_current_affairs",
            tags=["global", "breaking"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="nytimes-world",
            title="The New York Times - World",
            site_url="https://www.nytimes.com/section/world",
            feed_url="https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
            format="rss",
            category="news_current_affairs",
            tags=["global", "analysis"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="nytimes-homepage",
            title="The New York Times - Home Page",
            site_url="https://www.nytimes.com/",
            feed_url="https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            format="rss",
            category="news_current_affairs",
            tags=["global", "breaking"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="guardian-world",
            title="The Guardian - World",
            site_url="https://www.theguardian.com/world",
            feed_url="https://www.theguardian.com/world/rss",
            format="rss",
            category="news_current_affairs",
            tags=["global", "journalism"],
            language="en",
            region="EU-W",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="npr-world",
            title="NPR - World",
            site_url="https://www.npr.org/sections/world/",
            feed_url="https://feeds.npr.org/1004/rss.xml",
            format="rss",
            category="news_current_affairs",
            tags=["global", "journalism"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="cbc-world",
            title="CBC News - World",
            site_url="https://www.cbc.ca/news/world",
            feed_url="https://www.cbc.ca/cmlink/rss-world",
            format="rss",
            category="news_current_affairs",
            tags=["global", "breaking"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="bbc-top-news",
            title="BBC News - Top Stories",
            site_url="https://www.bbc.com/news",
            feed_url="https://feeds.bbci.co.uk/news/rss.xml",
            format="rss",
            category="news_current_affairs",
            tags=["global", "breaking"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="abc-au-news",
            title="ABC News (Australia)",
            site_url="https://www.abc.net.au/news/",
            feed_url="https://www.abc.net.au/news/feed/45910/rss.xml",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "breaking"],
            language="en",
            region="OC-AU",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="dw-top-stories",
            title="DW - Top Stories",
            site_url="https://www.dw.com/en/top-stories/s-9097",
            feed_url="https://rss.dw.com/xml/rss-en-all",
            format="rss",
            category="news_current_affairs",
            tags=["global", "journalism"],
            language="en",
            region="EU",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="france24-en",
            title="France 24 - English",
            site_url="https://www.france24.com/en/",
            feed_url="https://www.france24.com/en/rss",
            format="rss",
            category="news_current_affairs",
            tags=["global", "breaking"],
            language="en",
            region="EU-W",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="un-news",
            title="UN News",
            site_url="https://news.un.org/en/",
            feed_url="https://news.un.org/feed/subscribe/en/news/all/rss.xml",
            format="rss",
            category="international_development_aid",
            tags=["global", "humanitarian"],
            language="en",
            region="GLOBAL",
            source_type="government",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="times-of-india-world",
            title="Times of India - World",
            site_url="https://timesofindia.indiatimes.com/world",
            feed_url="https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "breaking"],
            language="en",
            region="AS-S",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="the-hindu-international",
            title="The Hindu - International",
            site_url="https://www.thehindu.com/news/international/",
            feed_url="https://www.thehindu.com/news/international/feeder/default.rss",
            format="rss",
            category="news_current_affairs",
            tags=["global", "analysis"],
            language="en",
            region="AS-S",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="le-monde-une",
            title="Le Monde - A la Une",
            site_url="https://www.lemonde.fr/",
            feed_url="https://www.lemonde.fr/rss/une.xml",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "journalism"],
            language="fr",
            region="EU-W",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="el-pais-portada",
            title="El Pais - Portada",
            site_url="https://elpais.com/",
            feed_url="https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "journalism"],
            language="es",
            region="EU-S",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="spiegel-international",
            title="Der Spiegel - International",
            site_url="https://www.spiegel.de/international/",
            feed_url="https://www.spiegel.de/international/index.rss",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "analysis"],
            language="en",
            region="EU-W",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="africanews",
            title="Africanews - Latest",
            site_url="https://www.africanews.com/",
            feed_url="https://www.africanews.com/feed/",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "breaking"],
            language="en",
            region="AF",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="allafrica-headlines",
            title="AllAfrica - Latest Headlines",
            site_url="https://allafrica.com/",
            feed_url="https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "journalism"],
            language="en",
            region="AF",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="times-of-israel",
            title="The Times of Israel",
            site_url="https://www.timesofisrael.com/",
            feed_url="https://www.timesofisrael.com/feed/",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "politics"],
            language="en",
            region="ME",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="mercopress",
            title="MercoPress",
            site_url="https://en.mercopress.com/",
            feed_url="https://en.mercopress.com/rss",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "journalism"],
            language="en",
            region="SA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="japan-times",
            title="The Japan Times",
            site_url="https://www.japantimes.co.jp/",
            feed_url="https://www.japantimes.co.jp/feed/",
            format="rss",
            category="news_current_affairs",
            tags=["regional", "journalism"],
            language="en",
            region="AS-E",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Politics and government
        FeedEntry(
            id="uk-gov-news",
            title="UK Government - News and Communications",
            site_url="https://www.gov.uk/search/news-and-communications",
            feed_url="https://www.gov.uk/search/news-and-communications.atom",
            format="atom",
            category="politics_government",
            tags=["policy", "government"],
            language="en",
            region="EU-W",
            source_type="government",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="un-press",
            title="United Nations - Press Releases",
            site_url="https://www.un.org/press/en/",
            feed_url="https://www.un.org/press/en/rss.xml",
            format="rss",
            category="international_relations_security",
            tags=["geopolitics", "policy"],
            language="en",
            region="GLOBAL",
            source_type="government",
            status="active",
            added=today,
        ),
        # Technology and startups
        FeedEntry(
            id="ars-technica",
            title="Ars Technica",
            site_url="https://arstechnica.com/",
            feed_url="http://feeds.arstechnica.com/arstechnica/index",
            format="rss",
            category="technology",
            tags=["hardware", "web"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="the-verge",
            title="The Verge",
            site_url="https://www.theverge.com/",
            feed_url="https://www.theverge.com/rss/index.xml",
            format="rss",
            category="technology",
            tags=["hardware", "digital-culture"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="wired",
            title="Wired",
            site_url="https://www.wired.com/",
            feed_url="https://www.wired.com/feed/rss",
            format="rss",
            category="technology",
            tags=["web", "digital-culture"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="mit-tech-review",
            title="MIT Technology Review",
            site_url="https://www.technologyreview.com/",
            feed_url="https://www.technologyreview.com/feed/",
            format="rss",
            category="technology",
            tags=["ai", "data-science"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="techcrunch",
            title="TechCrunch",
            site_url="https://techcrunch.com/",
            feed_url="https://techcrunch.com/feed/",
            format="rss",
            category="technology",
            tags=["startups", "venture-capital"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="hacker-news",
            title="Hacker News",
            site_url="https://news.ycombinator.com/",
            feed_url="https://news.ycombinator.com/rss",
            format="rss",
            category="technology",
            tags=["programming-languages", "open-source"],
            language="en",
            region="GLOBAL",
            source_type="community",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="google-research",
            title="Google Research Blog",
            site_url="https://research.google/blog/",
            feed_url="https://research.google/blog/rss/",
            format="rss",
            category="technology",
            tags=["ai", "machine-learning"],
            language="en",
            region="NA",
            source_type="corporate",
            status="active",
            added=today,
        ),
        # Cybersecurity
        FeedEntry(
            id="krebs-on-security",
            title="Krebs on Security",
            site_url="https://krebsonsecurity.com/",
            feed_url="https://krebsonsecurity.com/feed/",
            format="rss",
            category="cybersecurity_privacy",
            tags=["cybersecurity", "privacy"],
            language="en",
            region="NA",
            source_type="independent",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="the-hacker-news",
            title="The Hacker News",
            site_url="https://thehackernews.com/",
            feed_url="https://feeds.feedburner.com/TheHackersNews",
            format="rss",
            category="cybersecurity_privacy",
            tags=["cybersecurity", "privacy"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="securityweek",
            title="SecurityWeek",
            site_url="https://www.securityweek.com/",
            feed_url="https://www.securityweek.com/feed/",
            format="rss",
            category="cybersecurity_privacy",
            tags=["cybersecurity", "analysis"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="bleepingcomputer",
            title="BleepingComputer",
            site_url="https://www.bleepingcomputer.com/",
            feed_url="https://www.bleepingcomputer.com/feed/",
            format="rss",
            category="cybersecurity_privacy",
            tags=["cybersecurity", "privacy"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="cisa-alerts",
            title="CISA Alerts",
            site_url="https://www.cisa.gov/",
            feed_url="https://www.cisa.gov/uscert/ncas/alerts.xml",
            format="rss",
            category="cybersecurity_privacy",
            tags=["cybersecurity", "government"],
            language="en",
            region="NA",
            source_type="government",
            status="active",
            added=today,
        ),
        # Science and space
        FeedEntry(
            id="sciencedaily",
            title="ScienceDaily - Latest",
            site_url="https://www.sciencedaily.com/",
            feed_url="https://www.sciencedaily.com/rss/all.xml",
            format="rss",
            category="science_research",
            tags=["science", "research"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="nature",
            title="Nature",
            site_url="https://www.nature.com/",
            feed_url="https://www.nature.com/nature.rss",
            format="rss",
            category="science_research",
            tags=["science", "research"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="esa-activities",
            title="European Space Agency - Activities",
            site_url="https://www.esa.int/",
            feed_url="https://www.esa.int/rssfeed/Our_Activities",
            format="rss",
            category="science_research",
            tags=["space", "science"],
            language="en",
            region="EU",
            source_type="government",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="science-magazine",
            title="Science Magazine - News",
            site_url="https://www.science.org/news",
            feed_url="https://www.science.org/rss/news_current.xml",
            format="rss",
            category="science_research",
            tags=["science", "research"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Health and medicine
        FeedEntry(
            id="paho-news",
            title="PAHO - News",
            site_url="https://www.paho.org/en/news",
            feed_url="https://www.paho.org/en/rss.xml",
            format="rss",
            category="health_medicine",
            tags=["public-health", "medicine"],
            language="en",
            region="NA",
            source_type="ngo",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="cdc-newsroom",
            title="CDC - Newsroom",
            site_url="https://www.cdc.gov/media/",
            feed_url="https://tools.cdc.gov/api/v2/resources/media/132608.rss",
            format="rss",
            category="health_medicine",
            tags=["public-health", "medicine"],
            language="en",
            region="NA",
            source_type="government",
            status="active",
            added=today,
        ),
        # Agriculture and food systems
        FeedEntry(
            id="agfunder-news",
            title="AgFunderNews",
            site_url="https://agfundernews.com/",
            feed_url="https://agfundernews.com/feed",
            format="rss",
            category="agriculture_food_systems",
            tags=["agriculture", "food-systems"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Environment and climate
        FeedEntry(
            id="climate-gov",
            title="Climate.gov",
            site_url="https://www.climate.gov/",
            feed_url="https://www.climate.gov/rss.xml",
            format="rss",
            category="environment_climate",
            tags=["climate", "environment"],
            language="en",
            region="NA",
            source_type="government",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="unep-news",
            title="UNEP - News",
            site_url="https://www.unep.org/news-and-stories",
            feed_url="https://www.unep.org/rss.xml",
            format="rss",
            category="environment_climate",
            tags=["environment", "climate"],
            language="en",
            region="GLOBAL",
            source_type="ngo",
            status="active",
            added=today,
        ),
        # International development and humanitarian
        FeedEntry(
            id="unocha-news",
            title="UN OCHA - News",
            site_url="https://www.unocha.org/",
            feed_url="https://www.unocha.org/rss.xml",
            format="rss",
            category="international_development_aid",
            tags=["development", "humanitarian"],
            language="en",
            region="GLOBAL",
            source_type="government",
            status="active",
            added=today,
        ),
        # Energy
        FeedEntry(
            id="eia-today-in-energy",
            title="U.S. EIA - Today in Energy",
            site_url="https://www.eia.gov/todayinenergy/",
            feed_url="https://www.eia.gov/rss/todayinenergy.xml",
            format="rss",
            category="energy_systems",
            tags=["energy", "markets"],
            language="en",
            region="NA",
            source_type="government",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="oilprice",
            title="OilPrice.com",
            site_url="https://oilprice.com/",
            feed_url="https://oilprice.com/rss/main",
            format="rss",
            category="energy_systems",
            tags=["energy", "oil-gas"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Economics and finance
        FeedEntry(
            id="ecb-press",
            title="European Central Bank - Press Releases",
            site_url="https://www.ecb.europa.eu/press/pressreleases/html/index.en.html",
            feed_url="https://www.ecb.europa.eu/rss/press.html",
            format="rss",
            category="economics_macro_policy",
            tags=["economics", "policy"],
            language="en",
            region="EU",
            source_type="government",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="marketwatch-top",
            title="MarketWatch - Top Stories",
            site_url="https://www.marketwatch.com/",
            feed_url="https://feeds.marketwatch.com/marketwatch/topstories/",
            format="rss",
            category="finance_markets",
            tags=["markets", "finance"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
        FeedEntry(
            id="cnbc-top",
            title="CNBC - Top News",
            site_url="https://www.cnbc.com/world/?region=world",
            feed_url="https://www.cnbc.com/id/100003114/device/rss/rss.html",
            format="rss",
            category="finance_markets",
            tags=["markets", "finance"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Culture and arts
        FeedEntry(
            id="bbc-culture",
            title="BBC News - Entertainment & Arts",
            site_url="https://www.bbc.com/news/entertainment_and_arts",
            feed_url="https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
            format="rss",
            category="arts_entertainment",
            tags=["arts", "film-tv"],
            language="en",
            region="EU",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Transportation and infrastructure
        FeedEntry(
            id="aviation-week",
            title="Aviation Week",
            site_url="https://aviationweek.com/",
            feed_url="https://aviationweek.com/rss.xml",
            format="rss",
            category="transportation_infrastructure",
            tags=["transportation", "infrastructure"],
            language="en",
            region="GLOBAL",
            source_type="publisher",
            status="active",
            added=today,
        ),
        # Education
        FeedEntry(
            id="edsurge",
            title="EdSurge",
            site_url="https://www.edsurge.com/",
            feed_url="https://www.edsurge.com/rss",
            format="rss",
            category="education_learning",
            tags=["education", "web"],
            language="en",
            region="NA",
            source_type="publisher",
            status="active",
            added=today,
        ),
    ]

    return entries


def verify_feed(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Fetch a feed URL and confirm it looks like RSS/Atom."""
    request = Request(url, headers={"User-Agent": "rss-encyclopedia-seeder/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content = response.read(20000)
        encoding = response.headers.get("Content-Encoding", "").lower()
        if "gzip" in encoding:
            import gzip

            content = gzip.decompress(content)
        text = content.decode("utf-8", errors="ignore").lower()
        is_xml = "<rss" in text or "<feed" in text or "<rdf:rdf" in text
        return {
            "status": response.status,
            "ok": response.status == 200 and is_xml,
            "content_snippet": text[:200],
        }


def validate_entry(entry: FeedEntry, vocab: Dict[str, List[str]]) -> List[str]:
    """Validate the entry against the controlled vocabularies."""
    errors: List[str] = []
    if entry.category not in vocab["categories"]:
        errors.append(f"unknown category: {entry.category}")
    if entry.language not in vocab["languages"]:
        errors.append(f"unknown language: {entry.language}")
    if entry.region not in vocab["regions"]:
        errors.append(f"unknown region: {entry.region}")
    for tag in entry.tags:
        if tag not in vocab["tags"]:
            errors.append(f"unknown tag: {tag}")
    return errors


def write_feed(entry: FeedEntry, out_dir: Path) -> None:
    """Write a feed entry YAML file to disk."""
    out_path = out_dir / f"{entry.id}.yml"
    out_path.write_text(entry.to_yaml(), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the seeding script."""
    parser = argparse.ArgumentParser(description="Seed feed entries with verification.")
    parser.add_argument("--verify", action="store_true", help="Verify feed URLs before writing.")
    parser.add_argument("--write", action="store_true", help="Write feed files to data/feeds.")
    parser.add_argument("--out", type=str, help="Write JSON report to a file.")
    parser.add_argument("--offset", type=int, default=0, help="Start index for batch verification.")
    parser.add_argument("--limit", type=int, help="Limit entries for batch verification.")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout per feed request (seconds).")
    return parser.parse_args()


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    entries = feed_entries()
    if args.offset or args.limit is not None:
        start = max(args.offset, 0)
        end = start + args.limit if args.limit is not None else None
        entries = entries[start:end]
    vocab = load_vocab_ids()
    feeds_dir = ROOT / "data" / "feeds"

    report = []
    for entry in entries:
        entry_errors = validate_entry(entry, vocab)
        verification = None
        if args.verify:
            try:
                verification = verify_feed(entry.feed_url, timeout=args.timeout)
            except Exception as exc:
                verification = {"status": None, "ok": False, "error": str(exc)}

        report.append(
            {
                "id": entry.id,
                "title": entry.title,
                "errors": entry_errors,
                "verified": verification,
            }
        )

        if entry_errors:
            continue
        if args.verify and verification and not verification.get("ok"):
            continue
        if args.write:
            write_feed(entry, feeds_dir)

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")

    passed = [item for item in report if not item["errors"] and (not args.verify or item["verified"]["ok"])]
    print(f"Entries provided: {len(entries)}")
    print(f"Entries passing checks: {len(passed)}")


if __name__ == "__main__":
    main()
