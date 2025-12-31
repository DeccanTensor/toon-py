import json
import re
from typing import Any

# Characters that require a string to be quoted per TOON v3.0 spec
_NEEDS_QUOTING_RE = re.compile(r'[,:\[\]{}"\\"\n\r\t]')

# Patterns that would be misinterpreted as non-string types
_INT_PATTERN = re.compile(r"^-?\d+$")
_FLOAT_PATTERN = re.compile(
    r"^-?\d+\.\d+$|^-?\d+[eE][+-]?\d+$|^-?\d+\.\d+[eE][+-]?\d+$"
)
_TYPE_LITERALS = frozenset({"true", "false", "null"})


def _needs_quoting(val: str) -> bool:
    r"""
    Check if a string value needs to be quoted per TOON v3.0 spec.
    
    A string must be quoted if it:
    1. Contains special delimiter/syntax characters: , : [ ] { } " \ \n \r \t
    2. Looks like a type literal: true, false, null
    3. Looks like a number (int or float)
    4. Is empty (ambiguous)
    """
    if not val:
        # Empty string must be quoted to distinguish from missing value
        return True
    
    # Check for special characters
    if _NEEDS_QUOTING_RE.search(val):
        return True
    
    # Check for type literal confusion
    if val in _TYPE_LITERALS:
        return True
    
    # Check for numeric confusion
    if _INT_PATTERN.match(val) or _FLOAT_PATTERN.match(val):
        return True
    
    return False


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
            # Format logic per TOON v3.0 spec
            if val is None:
                s_val = "null"
            elif isinstance(val, bool):
                # Must check bool before int because bool is subclass of int in Python
                s_val = "true" if val else "false"
            elif isinstance(val, int):
                s_val = str(val)
            elif isinstance(val, float):
                s_val = str(val)
            elif isinstance(val, str):
                # TOON v3.0: Quote strings with special chars or type-like values
                if _needs_quoting(val):
                    s_val = json.dumps(val)
                else:
                    s_val = val
            elif isinstance(val, (dict, list)):
                # Embed JSON (object/array) directly
                s_val = json.dumps(val, ensure_ascii=False, separators=(",", ":"))
            else:
                # Fallback for other types - serialize as JSON string
                s_val = json.dumps(str(val))
            values.append(s_val)

        output.append("  " + ", ".join(values))

    return "\n".join(output)
