import re
from pathlib import Path


def load_yaml(path):
    try:
        import yaml  # type: ignore
    except Exception:
        return _load_simple_yaml(path)

    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _parse_scalar(value):
    text = value.strip()
    if text.startswith("\"") and text.endswith("\"") and len(text) >= 2:
        return text[1:-1]
    if text.startswith("'") and text.endswith("'") and len(text) >= 2:
        return text[1:-1]
    return text


def _load_simple_yaml(path):
    data = {}
    current_list_key = None
    current_list = None
    current_item = None
    list_mode = None

    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue

            indent = len(line) - len(line.lstrip(" "))
            content = line.lstrip(" ")

            if indent == 0:
                match = re.match(r"([A-Za-z0-9_-]+):(?:\s*(.*))?$", content)
                if not match:
                    continue
                key, value = match.group(1), match.group(2)
                if value is None or value == "":
                    data[key] = []
                    current_list_key = key
                    current_list = data[key]
                    current_item = None
                    list_mode = "list"
                else:
                    data[key] = _parse_scalar(value)
                    current_list_key = None
                    current_list = None
                    current_item = None
                    list_mode = None
                continue

            if indent == 2 and content.startswith("- "):
                if current_list is None:
                    continue
                item_content = content[2:].strip()
                if re.match(r"[A-Za-z0-9_-]+:\s*.*", item_content):
                    current_item = {}
                    current_list.append(current_item)
                    key, value = item_content.split(":", 1)
                    current_item[key.strip()] = _parse_scalar(value.strip())
                    list_mode = "list_of_maps"
                else:
                    current_list.append(_parse_scalar(item_content))
                    current_item = None
                continue

            if indent == 4 and list_mode == "list_of_maps" and current_item is not None:
                match = re.match(r"([A-Za-z0-9_-]+):\s*(.*)$", content)
                if match:
                    current_item[match.group(1)] = _parse_scalar(match.group(2))

    return data
