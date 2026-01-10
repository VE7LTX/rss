# Build Outputs

This project provides a build script to generate exported feed lists and indexes.

## Script

`scripts/build/generate_outputs.py`

## Requirements

- Python 3.10+
- PyYAML (`pip install pyyaml` or `pip install -r requirements.txt`) for full YAML support.
  The script falls back to a minimal parser if PyYAML is unavailable.

## Usage

```bash
python scripts/build/generate_outputs.py
```

Custom paths:

```bash
python scripts/build/generate_outputs.py --feeds-dir data/feeds --dist-dir dist
```

## Outputs

The script writes the following files under `dist/`:

- `feeds.json` — list of feed records
- `feeds.csv` — tabular export
- `feeds.opml` — importable OPML for RSS readers
- `indexes/index-by-tag.json`
- `indexes/index-by-category.json`
- `indexes/index-by-region.json`
- `indexes/index-by-source-type.json`
