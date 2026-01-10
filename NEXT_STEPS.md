# Next Steps

This document expands the roadmap into actionable, low-risk steps. Each step is ordered
so the project can progress without blocking future work.

## 1) Finalize Controlled Vocabularies

**Goal:** Lock in categories, tags, and locales so feed entries stay consistent.

- **Categories** (`data/categories.yml`)
  - Review for overlaps or missing global domains.
  - Keep the list stable; add new categories only when they enable major navigation wins.
- **Tags** (`data/tags.yml`)
  - Target 80–150 tags total; remove duplicates or ambiguous terms.
  - Prefer short, reusable tags over hyper-specific ones.
- **Locales** (`data/locales.yml`)
  - Extend languages and regions as new feeds require them.
  - Maintain ISO-like codes so filters remain predictable.

**Exit criteria:** Maintainers agree on vocabulary scope; changes require review.

---

## 2) Define the Feed Record Schema

**Goal:** Ensure each feed file has consistent required fields.

Proposed minimum fields for each feed entry:

- `id` (stable slug)
- `title`
- `site_url`
- `feed_url`
- `format` (rss | atom | json)
- `category` (single select)
- `tags` (multi-select)
- `language`
- `region`
- `source_type` (publisher, academic, gov, ngo, etc.)
- `status` (active, inactive, moved, dead)
- `added` (date)

**Exit criteria:** Schema is documented in `CONTRIBUTING.md` or a dedicated `docs/schema.md`.

---

## 3) Seed Initial Feeds

**Goal:** Add an initial set of feeds to validate the taxonomy and workflow.

- Start with **25–50 feeds** across 8–12 categories.
- Ensure regional coverage beyond North America and Europe.
- Include a mix of source types (publisher, academic, government, NGO, independent).

**Exit criteria:** A representative feed sample exists under `data/feeds/`.

---

## 4) Validation & Health Checks

**Goal:** Automate basic feed checks to keep the catalog clean.

Suggested checks:

- HTTP status and redirects
- Feed parse success (RSS/Atom/JSON)
- Last item date
- Minimum item count

**Exit criteria:** A simple validation script in `scripts/validate/` with JSON output.

---

## 5) Generate Outputs

**Goal:** Produce machine-friendly exports and indexes for filtering.

Outputs to generate in `dist/`:

- `feeds.opml`
- `feeds.json`
- `feeds.csv`
- `indexes/index-by-tag.json`
- `indexes/index-by-category.json`
- `indexes/index-by-region.json`
- `indexes/index-by-source-type.json`

**Exit criteria:** Build scripts create deterministic outputs from the feed registry.

---

## 6) Prototype a Simple Browser UI

**Goal:** Prove the filter model works at scale.

- Static HTML or lightweight JS
- Filters for category, tags, region, and source type
- Limit results to 20–25 items per view
- Display context (category, tags, region, source type) on each feed card

**Exit criteria:** A static demo that demonstrates faceted browsing on seeded data.

---

## 7) Live Updates Page (MVP)

**Goal:** Allow users to select feeds and view live updates.

- User selects feeds from filtered list
- Selected feeds render in a live-updating panel
- Save selections in local storage (initially)

**Exit criteria:** A basic “My Feeds” page that updates without reloading the registry.
