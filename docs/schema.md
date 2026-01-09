# Feed Record Schema

This document defines the minimum, required fields for each feed file in `data/feeds/`.

## Required Fields

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable slug. Use lowercase with hyphens. |
| `title` | string | Human-readable feed title. |
| `site_url` | string | Canonical site homepage URL. |
| `feed_url` | string | Direct RSS/Atom/JSON feed URL. |
| `format` | string | One of: `rss`, `atom`, `json`. |
| `category` | string | Single primary category from `data/categories.yml`. |
| `tags` | list | Multi-select tags from `data/tags.yml`. |
| `language` | string | Language code from `data/locales.yml` (BCP 47). |
| `region` | string | Region code from `data/locales.yml`. |
| `source_type` | string | One of: `publisher`, `independent`, `academic`, `ngo`, `government`, `think-tank`, `community`, `corporate`, `personal`. |
| `status` | string | One of: `active`, `inactive`, `moved`, `dead`. |
| `added` | string | Date added, ISO 8601 format (YYYY-MM-DD). |

## Optional Fields

| Field | Type | Notes |
| --- | --- | --- |
| `description` | string | Short description of the feed. |
| `notes` | string | Additional context for curators. |
| `last_verified` | string | Date of last validation check. |
| `homepage_language` | string | If different from feed language. |
| `aliases` | list | Alternate feed URLs (if migrated or mirrored). |

## Example

```yaml
id: example-news
title: Example News
site_url: https://example.com
feed_url: https://example.com/feed.xml
format: rss
category: news_current_affairs
tags:
  - breaking
  - local
language: en
region: NA
source_type: publisher
status: active
added: "2026-01-08"
```

## File Naming

- One feed per file.
- File name should match the `id` (e.g., `example-news.yml`).
- Place files in `data/feeds/` (optionally in subfolders by category later).
