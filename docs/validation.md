# Feed Validation

This project includes a lightweight validation script to check required fields in
`data/feeds/`.

## Script

`scripts/validate/validate_feeds.py`

## Requirements

- Python 3.10+
- PyYAML (`pip install pyyaml` or `pip install -r requirements.txt`) for full YAML support.
  The script falls back to a minimal parser if PyYAML is unavailable.

## Usage

```bash
python scripts/validate/validate_feeds.py
```

Optional JSON output:

```bash
python scripts/validate/validate_feeds.py --json
```

## What It Checks

- Required fields from the schema (`docs/schema.md`)
- `tags` field must be a list

## Exit Codes

- `0` when all feeds pass validation
- `1` when any feed fails validation
