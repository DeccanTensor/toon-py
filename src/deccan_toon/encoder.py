import json
from typing import Any


def dumps(data: list[dict[str, Any]]) -> str:
    """Serializes a list of dicts to a TOON string."""
    if not data:
        return ""

    # 1. Extract Header (Schema)
    # Use a stable union-of-keys across all rows so "mixed schema" inputs don't crash.
    keys: list[str] = []
    seen: set[str] = set()
    for row in data:
        for k in row.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)

    # 2. Build Header Line: items[count]{key1,key2}:
    count = len(data)
    header_keys = ",".join(keys)
    output = [f"items[{count}]{{{header_keys}}}:"]

    # 3. Build Rows
    for row in data:
        values = []
        for k in keys:
            val = row.get(k)
            # Format logic
            if val is None:
                s_val = "null"
            elif isinstance(val, bool):
                s_val = str(val).lower()
            elif isinstance(val, (int, float)):
                s_val = str(val)
            elif isinstance(val, str) and ("," in val or "\n" in val or '"' in val):
                # Quote strings that would break row splitting.
                # NOTE: uses JSON string escaping (\", \n, etc.).
                s_val = json.dumps(val)
            elif isinstance(val, (dict, list)):
                # Embed JSON (object/array) directly. Decoder must understand nested brackets/braces.
                s_val = json.dumps(
                    val, ensure_ascii=False, separators=(",", ":")
                )
            else:
                s_val = str(val) if isinstance(val, str) else json.dumps(val)
            values.append(s_val)

        output.append("  " + ", ".join(values))

    return "\n".join(output)
