"""
Unit tests for the build pipeline.

These tests confirm output artifacts are created from a minimal registry dataset.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build.build import build_all


def write_file(path: Path, content: str) -> None:
    """Write a file with consistent UTF-8 encoding."""
    path.write_text(content.strip() + "\n", encoding="utf-8")


class BuildTests(unittest.TestCase):
    """Coverage for build outputs and artifact creation."""

    def test_build_outputs(self) -> None:
        """Build should create expected dist outputs for a minimal dataset."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            feeds_dir = data_dir / "feeds"
            feeds_dir.mkdir(parents=True)

            write_file(
                data_dir / "categories.yml",
                """
version: 1
categories:
  - id: news_current_affairs
    title: "News & Current Affairs"
""",
            )
            write_file(
                data_dir / "tags.yml",
                """
version: 1
tags:
  - id: breaking
    title: "Breaking"
""",
            )
            write_file(
                data_dir / "locales.yml",
                """
version: 1
languages:
  - code: en
    name: English
regions:
  - code: GLOBAL
    name: Global
""",
            )
            write_file(
                feeds_dir / "example.yml",
                """
id: example
title: Example News
site_url: https://example.com
feed_url: https://example.com/feed.xml
format: rss
category: news_current_affairs
tags:
  - breaking
language: en
region: GLOBAL
source_type: publisher
status: active
added: "2026-01-08"
""",
            )

            summary = build_all(root)

            self.assertEqual(summary.feed_count, 1)
            self.assertTrue((summary.dist_dir / "feeds.json").exists())
            self.assertTrue((summary.dist_dir / "feeds.csv").exists())
            self.assertTrue((summary.dist_dir / "feeds.opml").exists())
            self.assertTrue((summary.dist_dir / "items.json").exists())
            self.assertTrue((summary.dist_dir / "indexes" / "index-by-tag.json").exists())

            data = json.loads((summary.dist_dir / "feeds.json").read_text(encoding="utf-8"))
            self.assertEqual(len(data["feeds"]), 1)


if __name__ == "__main__":
    unittest.main()
