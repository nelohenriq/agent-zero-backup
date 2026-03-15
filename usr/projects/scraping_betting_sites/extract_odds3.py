import json

with open("processed_sports/solverde_ws_live_20260307_161713.json") as f:
    data = json.load(f)

ws_frames = data.get("websocket_frames", [])
matches = []
for frame in ws_frames:
    if frame.get("direction") == "received":
        payload = frame.get("data", "")
        if "\"s\":" in payload and "marketLines" in payload:
            parts = payload.split("\n\n", 1)
            if len(parts) > 1:
                try:
                    event_data = json.loads(parts[1])
                    for event_id, event in event_data.items():
                        if "s" in event:
                            sport = event["s"]
                            matches.append({
                                "id": sport.get("id"),
                                "name": sport.get("name"),
                                "sportId": sport.get("sportId"),
                                "className": sport.get("className"),
                                "marketCount": len(sport.get("marketLines", {}))
                            })
                except:
                    pass
print(f"Found {len(matches)} match events with betting data:")
for m in matches[:10]:
    print(f" - {m["name"]} ({m["className"]}) - {m["marketCount"]} markets")
