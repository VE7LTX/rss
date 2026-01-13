# Testing

## Document header

- Purpose: Validate the registry pipeline and confirm deterministic outputs.
- Audience: Contributors and maintainers.
- Scope: Unit tests, validation, health checks, and build verification.
- Last updated: 2026-01-13.

## Unit tests

```bash
python -m pytest
```

Legacy unittest runner:

```bash
python -m unittest discover -s tests
```

## Validation script

```bash
python scripts/validate/validate.py
```

## Health checks (network)

```bash
python scripts/validate/validate.py --health --health-timeout 20
```

Use `--offset` and `--limit` to run batches.
Use `--out report.json` to write a structured report.

## Build script

```bash
python scripts/build/build.py
```

## Expected outputs

- Validation exits non-zero on errors.
- Build writes outputs to `dist/` and prints the feed count.
- Health checks print per-feed errors when a feed is unreachable or has no items.
