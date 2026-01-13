# The RSS Encyclopedia

A structured registry of RSS/Atom/JSON feeds with rich metadata, designed to scale to hundreds or thousands of sources. It ships with validation tooling, deterministic build outputs, and a static prototype UI for faceted browsing.

This project treats feeds as data, not bookmarks.

## What you get

- Curated feed metadata with controlled vocabularies (categories, tags, locales)
- Validation tooling to keep entries consistent
- Build outputs (JSON, CSV, OPML, indexes)
- A static UI for filtering and previewing selections
- Unit tests to verify the core pipeline

## Quickstart

Requirements: Python 3.9+.

```bash
# From the repo root
python scripts/validate/validate.py
python scripts/build/build.py
python -m http.server 8000
```

Open `http://localhost:8000/public/index.html`.

## Documentation

- Setup and startup: `setup.md`
- Feed schema: `docs/schema.md`
- UI usage: `docs/prototype.md`
- Testing guidance: `docs/testing.md`
- Roadmap and sequencing: `NEXT_STEPS.md`

## Project layout

```
C:\rss\
  data\
    feeds\
    categories.yml
    tags.yml
    locales.yml
  docs\
    schema.md
    prototype.md
    testing.md
  scripts\
    lib\
    validate\
    build\
  dist\
    feeds.opml
    feeds.json
    feeds.csv
    items.json
    indexes\
  public\
    index.html
    styles.css
    app.js
  tests\
    test_build.py
    test_validate.py
    test_yamlish.py
  README.md
  NEXT_STEPS.md
  setup.md
```

## Data model

Each feed record is stored as one YAML file in `data/feeds/` and follows the schema in `docs/schema.md`.

Required fields include:
- `id`, `title`, `site_url`, `feed_url`, `format`
- `category`, `tags`, `language`, `region`
- `source_type`, `status`, `added`

## Outputs

The build step generates deterministic outputs in `dist/`:

- `feeds.json` for apps/dashboards
- `feeds.csv` for analysis
- `feeds.opml` for feed readers
- `indexes/*` for fast filtering
- `items.json` demo items for the prototype UI

## The RSS Encyclopedia UI

The RSS Encyclopedia UI is a static site in `public/` that loads data from `dist/`. It supports:
- Faceted filtering (category, tags, region, source type)
- Search across metadata
- Feed selection with local storage persistence
- Demo "Live Updates" panel using generated items

See `docs/prototype.md` for details.

## Testing

```bash
python -m unittest discover -s tests
```

## Contributing

- One feed per file
- Use the controlled vocabularies in `data/`
- Run validation and tests before submitting changes

More guidance: `NEXT_STEPS.md`.

## License

Open and permissive. Details TBD.
