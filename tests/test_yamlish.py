"""
Unit tests for the YAML helper.

These tests focus on the fallback parser, which must handle the repo's
simple YAML structures without external dependencies.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.lib.yamlish import load_yaml


class YamlishTests(unittest.TestCase):
    """Coverage for the fallback YAML loader."""

    def test_load_yaml_simple_mapping(self) -> None:
        """Ensure simple mappings and list-of-maps parse correctly."""
        content = """
version: 1
categories:
  - id: news
    title: "News"
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.yml"
            path.write_text(content.strip() + "\n", encoding="utf-8")

            data = load_yaml(path)

        self.assertEqual(str(data["version"]), "1")
        self.assertEqual(data["categories"][0]["id"], "news")
        self.assertEqual(data["categories"][0]["title"], "News")


if __name__ == "__main__":
    unittest.main()
