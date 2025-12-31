import json
import re
from typing import Any

from .errors import TOONDecodeError

_INT_RE = re.compile(r"^-?\d+$")


def _split_row_values(line: str) -> list[str]:
    """
    Split a row by commas, but ignore commas inside JSON-quoted strings.

    Encoder uses json.dumps for quoted strings (\", \\n, etc.), so we must respect
    backslash escaping while inside quotes.
    """
    out: list[str] = []
    buf: list[str] = []
    in_quotes = False
    escaped = False
    brace_depth = 0
    bracket_depth = 0

    for ch in line:
        if in_quotes:
            buf.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_quotes = False
            continue

        # not in quotes
        if ch == "{":
            brace_depth += 1
            buf.append(ch)
            continue
        if ch == "}":
            brace_depth -= 1
            if brace_depth < 0:
                msg = "Malformed JSON-like value in row (unbalanced '}')"
                raise TOONDecodeError(msg)
            buf.append(ch)
            continue
        if ch == "[":
            bracket_depth += 1
            buf.append(ch)
            continue
        if ch == "]":
            bracket_depth -= 1
            if bracket_depth < 0:
                msg = "Malformed JSON-like value in row (unbalanced ']')"
                raise TOONDecodeError(msg)
            buf.append(ch)
            continue

        if ch == "," and brace_depth == 0 and bracket_depth == 0:
            out.append("".join(buf).strip())
            buf = []
            continue
        if ch == '"':
            in_quotes = True
            buf.append(ch)
            continue

        buf.append(ch)

    if in_quotes:
        raise TOONDecodeError("Malformed quoted value in row")
    if brace_depth != 0 or bracket_depth != 0:
        msg = "Malformed JSON-like value in row (unbalanced brackets/braces)"
        raise TOONDecodeError(msg)

    out.append("".join(buf).strip())
    return out


def loads(toon_str: str) -> list[dict[str, Any]]:
    """Parses a TOON string back to a list of dicts."""
    if not toon_str or not toon_str.strip():
        return []

    lines = toon_str.strip().splitlines()
    header_line = lines[0].strip()

    # 1. Parse Keys
    match = re.search(r"\{([^}]+)\}", header_line)
    if not match:
        raise TOONDecodeError("Invalid header: missing or malformed key block")
    keys = [k.strip() for k in match.group(1).split(",")]
    if any(not k for k in keys):
        raise TOONDecodeError("Invalid header: empty key name")

    # 2. Parse Rows
    result = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        raw_values = _split_row_values(line)
        if len(raw_values) != len(keys):
            msg = (
                f"Row width mismatch: expected {len(keys)} columns, "
                f"got {len(raw_values)}"
            )
            raise TOONDecodeError(msg)

        row_dict = {}
        for i, key in enumerate(keys):
            val_str = raw_values[i]

            # Type conversion
            if val_str == "null":
                val = None
            elif val_str == "true":
                val = True
            elif val_str == "false":
                val = False
            elif _INT_RE.match(val_str):
                val = int(val_str)
            elif val_str.startswith('"'):
                try:
                    val = json.loads(val_str)
                except json.JSONDecodeError as e:
                    raise TOONDecodeError(f"Invalid JSON string value: {e.msg}") from e
            elif val_str.startswith("{") or val_str.startswith("["):
                try:
                    val = json.loads(val_str)
                except json.JSONDecodeError as e:
                    raise TOONDecodeError(f"Invalid JSON value: {e.msg}") from e
            else:
                try:
                    val = float(val_str)
                except ValueError:
                    val = val_str

            row_dict[key] = val
        result.append(row_dict)

    return result
