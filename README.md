# The RSS Encyclopedia Registry & Feed Browser

A structured, open registry of RSS / Atom / JSON feeds, designed to scale to **hundreds or thousands of sources**, with tooling to **browse, filter, and select feeds for live updates** on a personalized page.

This project treats RSS feeds as **data**, not bookmarks.

---

## What This Is

- A curated catalog of RSS feeds with rich metadata
- A navigation layer that makes large feed collections usable
- A foundation for building a browser-like experience for RSS
- Exportable to common formats (OPML, JSON, CSV)

Users don’t scroll endless lists.  
They filter, select, and subscribe.

---

## What This Is Not

- Not a feed reader replacement (yet)
- Not a scraper or content mirror
- Not an algorithmic ranking engine
- Not tied to any single UI or platform

This repo provides structure and truth.  
Readers, dashboards, and apps consume it.

---

## Core Idea

Instead of folders and long lists, feeds are navigated using facets:

- Category (what domain it belongs to)
- Tags (what it’s about)
- Region / Locale (where it’s relevant)
- Source Type (who publishes it)
- Activity / Health (how alive it is)

This allows users to do things like:

- “AI + policy + Europe”
- “Cybersecurity + government + active”
- “Local news + Canada”
- “Academic research + climate”

---

## Intended User Experience (High Level)

1. User browses feeds using filters
2. User selects a small set of feeds
3. Selected feeds appear on a live updates page
4. Updates refresh without reloading the entire catalog

Think:
“A browser for RSS feeds, not a dumping ground.”

---

## Repository Structure

```
rss-registry/
  data/
    feeds/
    categories.yml
    tags.yml
    locales.yml
  docs/
    schema.md
    validation.md
    adding-feeds.md
    build.md
    ui.md
  scripts/
    validate/
    build/
  dist/
    feeds.opml
    feeds.json
    feeds.csv
    indexes/
  web/
    index.html
    styles.css
    app.js
  README.md
  CONTRIBUTING.md
  NEXT_STEPS.md
```

---

## Feed Metadata Model (Simplified)

Each feed includes:

- Title and site URL
- Feed URL and format
- Primary category
- Multiple tags
- Region and language
- Source type (publisher, academic, gov, etc.)
- Activity status (derived, not manual)

Feeds are filterable, comparable, and auditable.

Full schema details: [`docs/schema.md`](docs/schema.md).

---

## Adding Feeds

Guidance for formatting and submission lives in [`docs/adding-feeds.md`](docs/adding-feeds.md).

---

## Validation

A lightweight validation script checks required fields in `data/feeds/`.

Documentation: [`docs/validation.md`](docs/validation.md).

---

## Build Outputs

Export generation and index building are documented in [`docs/build.md`](docs/build.md).

---

## Browser UI Prototype

A static browser prototype lives in `web/`.

Documentation: [`docs/ui.md`](docs/ui.md).

---

## Navigation Model

Feeds are explored using orthogonal filters, not nesting:

- Category (single-select)
- Tags (multi-select)
- Region / Locale
- Source Type
- Activity Status

Lists are intentionally short.  
Counts and context are always shown.

---

## Outputs

The registry generates:

- OPML for feed readers
- JSON for apps and dashboards
- CSV for analysis
- Precomputed indexes for fast filtering

All outputs are deterministic and reproducible.

---

## Why This Exists

Most RSS lists fail because they:
- Become unmaintainable
- Collapse under scale
- Assume users want everything
- Treat feeds like bookmarks instead of sources

This project assumes:
- Users want signal
- Trust varies by source
- Geography matters
- Activity matters
- Control beats algorithms

---

## Contribution Philosophy

- One feed per file
- Clear metadata over clever naming
- No affiliate links
- Prefer official feeds
- Validation is automated
- Humans curate, machines verify

See CONTRIBUTING.md for details.

---

## Status

Early structure and taxonomy phase.  
Focus is on getting the model right before building UI.

---

## Next Steps

Detailed notes for the next milestones live in [`NEXT_STEPS.md`](NEXT_STEPS.md).

---

## Roadmap (High Level)

- Finalize global category and tag sets
- Seed with high-signal feeds
- Automated validation and health checks
- Static browsing UI
- User-selectable live feed views

---

## License

Open and permissive.  
Details TBD.
