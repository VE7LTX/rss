# Testing

Purpose: Validate the registry pipeline and ensure deterministic outputs.

## Unit tests

```bash
python -m unittest discover -s tests
```

## Validation script

```bash
python scripts/validate/validate.py
```

## Build script

```bash
python scripts/build/build.py
```

## Expected outputs

- Validation exits non-zero on errors.
- Build writes outputs to `dist/` and prints the feed count.
