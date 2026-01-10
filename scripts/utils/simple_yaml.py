"""Minimal YAML loader for simple feed files.

Supports:
- top-level key: value pairs
- lists of scalars (dash-prefixed)
"""

from __future__ import annotations

from typing import Any, Dict


def load_simple_yaml(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("-"):
            if current_list_key is None:
                raise ValueError("List item without a key")
            item = line.lstrip("-").strip()
            data[current_list_key].append(item)
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value == "":
                data[key] = []
                current_list_key = key
            else:
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                data[key] = value
                current_list_key = None
            continue

        raise ValueError(f"Unsupported YAML line: {raw_line}")

    return data
