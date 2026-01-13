"""
Unit tests for feed parsing helpers.
"""

from __future__ import annotations

import unittest

from scripts.server.server import parse_items


RSS_SAMPLE = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Example RSS Item</title>
      <link>https://example.com/rss-item</link>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""

ATOM_SAMPLE = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Example Atom Entry</title>
    <link href="https://example.com/atom-entry" />
    <updated>2024-01-01T12:00:00Z</updated>
  </entry>
</feed>
"""


class FeedParserTests(unittest.TestCase):
    """Ensure RSS and Atom parsing returns normalized items."""

    def test_parse_rss(self) -> None:
        items = parse_items(RSS_SAMPLE)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Example RSS Item")

    def test_parse_atom(self) -> None:
        items = parse_items(ATOM_SAMPLE)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Example Atom Entry")


if __name__ == "__main__":
    unittest.main()
