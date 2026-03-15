import json
import glob

# Find network captures with actual HTTP responses
files = (glob.glob('solverde*network*.json') + 
         glob.glob('processed_sports/*intercept*.json') + 
         glob.glob('processed_sports/*capture*.json'))

print("=== Looking for HTTP responses with data ===")
for f in sorted(files)[-10:]:
    try:
        with open(f) as fp:
            data = json.load(fp)
        if isinstance(data, list):
            print(f"\n{f}: list with {len(data)} items")
            # Check if any item has response data
            for item in data[:3]:
                if isinstance(item, dict) and 'response' in item:
                    print(f" Has response: {type(item.get('response'))}")
        elif isinstance(data, dict):
            keys = list(data.keys())[:5]
            print(f"\n{f}: dict keys = {keys}")
            # Check for any large data
            for k, v in data.items():
                if isinstance(v, (list, dict)):
                    print(f" {k}: {type(v).__name__} with {len(v) if hasattr(v, '__len__') else 'N/A'} items")
    except Exception as e:
        print(f"Error {f}: {e}")
