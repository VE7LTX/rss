# Adding Feeds

This guide explains how to add new feeds, how to format YAML correctly, and how to
validate submissions.

## YAML Formatting Rules

Each feed is a single YAML file in `data/feeds/`. Follow these formatting rules:

- **Two-space indentation** (no tabs).
- **Lowercase keys** with underscores.
- **Strings** should be plain unless they contain special characters; use quotes when in doubt.
- **Dates** must be quoted in ISO 8601 format: `"YYYY-MM-DD"`.
- **Lists** use hyphen-prefixed items.

Example:

```yaml
id: example-feed
title: Example Feed
site_url: https://example.com
feed_url: https://example.com/rss.xml
format: rss
category: news_current_affairs
tags:
  - breaking
  - global
language: en
region: GLOBAL
source_type: publisher
status: active
added: "2026-01-08"
```

## Where to Place Files

- Save each feed as `data/feeds/<id>.yml`.
- The filename **must match** the `id` field.

## Required Fields

See the full schema in [`docs/schema.md`](schema.md). Required fields include:

- `id`, `title`, `site_url`, `feed_url`
- `format`, `category`, `tags`
- `language`, `region`
- `source_type`, `status`, `added`

## How to Choose Categories & Tags

- **Category:** exactly one value from `data/categories.yml`.
- **Tags:** multiple values from `data/tags.yml`.
- Prefer **broad, reusable tags** over niche tags.
- Avoid adding new tags without review unless truly necessary.

## Source Type Guidance

Use one of the defined `source_type` values:

- `publisher`
- `independent`
- `academic`
- `ngo`
- `government`
- `think-tank`
- `community`
- `corporate`
- `personal`

## Verification Checklist

Before committing a new feed, confirm:

1. **URL works** — `feed_url` returns a valid RSS/Atom/JSON feed.
2. **Format is correct** — set `format` to `rss`, `atom`, or `json`.
3. **Category + tags** match the feed’s primary focus.
4. **Locale accuracy** — language and region are correct.
5. **Schema compliance** — all required fields are present.

## Validation Script

Run the validation script to catch missing or malformed fields:

```bash
python scripts/validate/validate_feeds.py
```

For JSON output:

```bash
python scripts/validate/validate_feeds.py --json
```
