
import json
import os

def json_to_toon(data, indent=0):
    lines = []
    sp = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                fields = list(v[0].keys())
                header = f"{k}[{len(v)}]{{{','.join(fields)}}}:"
                lines.append(f"{sp}{header}")
                for item in v:
                    row = ",".join(str(item.get(f, '')).replace(',', ' ') for f in fields)
                    lines.append(f"{sp}  {row}")
            elif isinstance(v, (dict, list)):
                lines.append(f"{sp}{k}:")
                lines.extend(json_to_toon(v, indent + 1))
            else:
                lines.append(f"{sp}{k}: {v}")
    return "\n".join(lines)
