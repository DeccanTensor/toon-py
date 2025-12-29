import re
import json
from typing import List, Dict, Any


def loads(toon_str: str) -> List[Dict[str, Any]]:
    """Parses a TOON string back to a list of dicts."""
    if not toon_str or not toon_str.strip():
        return []

    lines = toon_str.strip().splitlines()
    header_line = lines[0].strip()

    # 1. Parse Keys
    match = re.search(r"\{([^}]+)\}", header_line)
    if not match:
        raise ValueError("Invalid Header")
    keys = [k.strip() for k in match.group(1).split(",")]

    # 2. Parse Rows
    result = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        # Split by comma but ignore commas inside quotes
        pattern = r'(?:^|,)\s*("(?:[^"]|"")*"|[^,]*)'
        raw_values = [m.strip().strip(",") for m in re.findall(pattern, line) if m]

        row_dict = {}
        for i, key in enumerate(keys):
            val_str = raw_values[i] if i < len(raw_values) else "null"

            # Type conversion
            if val_str == "null":
                val = None
            elif val_str == "true":
                val = True
            elif val_str == "false":
                val = False
            elif val_str.isdigit():
                val = int(val_str)
            elif val_str.startswith('"'):
                try:
                    val = json.loads(val_str)
                except:
                    val = val_str
            else:
                try:
                    val = float(val_str)
                except:
                    val = val_str

            row_dict[key] = val
        result.append(row_dict)

    return result
