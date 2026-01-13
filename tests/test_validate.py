"""
Unit tests for the validation pipeline.

These tests validate a minimal registry payload using temporary directories.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate.validate import load_vocab, validate_all


def write_file(path: Path, content: str) -> None:
    """Write a file with consistent UTF-8 encoding."""
    path.write_text(content.strip() + "\n", encoding="utf-8")


class ValidationTests(unittest.TestCase):
    """Coverage for registry validation helpers."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data_dir = self.root / "data"
        self.feeds_dir = self.data_dir / "feeds"
        self.feeds_dir.mkdir(parents=True)

        write_file(
            self.data_dir / "categories.yml",
            """
version: 1
categories:
  - id: news_current_affairs
    title: "News & Current Affairs"
""",
        )
        write_file(
            self.data_dir / "tags.yml",
            """
version: 1
tags:
  - id: breaking
    title: "Breaking"
""",
        )
        write_file(
            self.data_dir / "locales.yml",
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

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_validate_all_success(self) -> None:
        """A valid feed should pass validation without errors."""
        write_file(
            self.feeds_dir / "example.yml",
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

        vocab = load_vocab(self.data_dir)
        report = validate_all(self.feeds_dir, vocab)

        self.assertEqual(report.errors, 0)
        self.assertEqual(report.warnings, 0)
        self.assertEqual(report.feeds_checked, 1)

    def test_validate_all_missing_required_field(self) -> None:
        """Missing required fields should raise validation errors."""
        write_file(
            self.feeds_dir / "bad.yml",
            """
id: bad
title: Bad Feed
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
""",
        )

        vocab = load_vocab(self.data_dir)
        report = validate_all(self.feeds_dir, vocab)

        self.assertGreater(report.errors, 0)
        self.assertEqual(report.feeds_checked, 1)


if __name__ == "__main__":
    unittest.main()
