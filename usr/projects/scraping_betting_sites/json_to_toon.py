import json
import sys

def json_to_toon(data, indent=0):
    """Convert a JSON-serializable object to TOON format."""
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            key_str = str(key)
            # Check if key needs quoting
            if "," in key_str or key_str.strip() != key_str:
                key_str = f'"{key_str}"'
            
            if isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Tabular array of objects
                    field_names = list(value[0].keys())
                    lines.append(f"{'  ' * indent}{key_str}[{len(value)}]{{{','.join(field_names)}}}:")
                    for item in value:
                        row_values = [str(item.get(field, '')) for field in field_names]
                        lines.append(f"{'  ' * (indent + 1)}{','.join(row_values)}")
                else:
                    # Simple array
                    lines.append(f"{'  ' * indent}{key_str}[{len(value)}]:")
                    for item in value:
                        if isinstance(item, (dict, list)):
                            lines.append(json_to_toon(item, indent + 1))
                        else:
                            item_str = str(item)
                            if "," in item_str or item_str.strip() != item_str:
                                item_str = f'"{item_str}"'
                            lines.append(f"{'  ' * (indent + 1)}{item_str}")
            elif isinstance(value, dict):
                lines.append(f"{'  ' * indent}{key_str}:")
                lines.append(json_to_toon(value, indent + 1))
            else:
                value_str = str(value)
                if "," in value_str or value_str.strip() != value_str:
                    value_str = f'"{value_str}"'
                lines.append(f"{'  ' * indent}{key_str}: {value_str}")
        return '\n'.join(lines)
    elif isinstance(data, list):
        lines = [f"[{len(data)}]:"]
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(json_to_toon(item, indent + 1))
            else:
                item_str = str(item)
                if "," in item_str or item_str.strip() != item_str:
                    item_str = f'"{item_str}"'
                lines.append(f"{'  ' * (indent + 1)}{item_str}")
        return '\n'.join(lines)
    else:
        return f"{'  ' * indent}{data}"

def convert_file(json_file, toon_file):
    """Convert JSON file to TOON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        toon_content = json_to_toon(data)
        
        with open(toon_file, 'w', encoding='utf-8') as f:
            f.write(toon_content)
        
        print(f"Successfully converted {json_file} -> {toon_file}")
        
        # Calculate compression ratio
        import os
        json_size = os.path.getsize(json_file)
        toon_size = os.path.getsize(toon_file)
        ratio = (1 - toon_size / json_size) * 100 if json_size > 0 else 0
        print(f"JSON: {json_size} bytes, TOON: {toon_size} bytes")
        print(f"Compression ratio: {ratio:.1f}% reduction")
        
    except Exception as e:
        print(f"Error converting {json_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_to_toon.py <json_file1> [json_file2 ...]")
        print("Converts JSON files to TOON format with .toon extension")
        sys.exit(1)
    
    for json_file in sys.argv[1:]:
        if not json_file.endswith('.json'):
            print(f"Skipping {json_file}: not a .json file")
            continue
            
        toon_file = json_file.rsplit('.', 1)[0] + '.toon'
        convert_file(json_file, toon_file)
