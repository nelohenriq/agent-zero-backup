import asyncio
import websockets
import json

def connect_frame(host):
    return f"CONNECT\nhost:{host}\nprotocol-version:1.5\naccept-version:1.2,1.1,1.0\nheart-beat:10000,10000\n\n\x00"

def subscribe_frame(destination, sub_id):
    return f"SUBSCRIBE\nid:{sub_id}\ndestination:{destination}\nlocale:pt\n\n\x00"

async def debug():
    host = "sportswidget.placard.pt"
    url = f"wss://{host}/api/websocket"
    topic = "/api/eventgroups/soccer-live-match-events-small"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://www.placard.pt"
    }

    try:
        async with websockets.connect(url, additional_headers=headers, subprotocols=["v10.stomp", "v11.stomp", "v12.stomp"]) as ws:
            await ws.send(connect_frame(host))
            await ws.recv() # CONNECTED
            await ws.send(subscribe_frame(topic, "debug-sub"))
            
            while True:
                msg = await ws.recv()
                if msg.startswith("MESSAGE"):
                    body = msg.split("\n\n", 1)[1].split("\x00", 1)[0]
                    data = json.loads(body)
                    # Print a significant portion of the first match object
                    if isinstance(data, list) and len(data) > 0:
                        print(json.dumps(data[0], indent=2))
                    else:
                        print(json.dumps(data, indent=2))
                    break
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(debug())
