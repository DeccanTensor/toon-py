import json
from typing import List, Dict, Any

def dumps(data: List[Dict[str, Any]]) -> str:
    """Serializes a list of dicts to a TOON string."""
    if not data:
        return ""

    # 1. Extract Header (Schema)
    keys = list(data[0].keys())
    
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
            if val is None: s_val = "null"
            elif isinstance(val, bool): s_val = str(val).lower()
            elif isinstance(val, (int, float)): s_val = str(val)
            elif isinstance(val, str) and ("," in val or "\n" in val):
                s_val = json.dumps(val) # Quote complex strings
            else:
                s_val = str(val) if isinstance(val, str) else json.dumps(val)
            values.append(s_val)
        
        output.append("  " + ", ".join(values))

    return "\n".join(output)