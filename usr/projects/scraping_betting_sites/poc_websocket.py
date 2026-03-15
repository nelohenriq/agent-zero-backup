import asyncio
import websockets
import json
import time

# STOMP frames construction helpers
def connect_frame(host):
    # Replicating the browser's CONNECT frame exactly as seen in logs
    # Adding 'host' which is mandatory for STOMP 1.1/1.2
    return f"CONNECT\nhost:{host}\nprotocol-version:1.5\naccept-version:1.2,1.1,1.0\nheart-beat:10000,10000\n\n\x00"

def subscribe_frame(destination, sub_id):
    # Replicating the browser's SUBSCRIBE frame
    return f"SUBSCRIBE\nid:{sub_id}\ndestination:{destination}\nlocale:pt\n\n\x00"

async def run_poc():
    host = "sportswidget.placard.pt"
    url = f"wss://{host}/api/websocket"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://www.placard.pt",
        "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    try:
        print(f"Connecting to {url}...")
        # Specify subprotocols common for STOMP
        async with websockets.connect(
            url, 
            additional_headers=headers, 
            subprotocols=["v10.stomp", "v11.stomp", "v12.stomp"]
        ) as ws:

            # Send CONNECT
            await ws.send(connect_frame(host))

            # Wait for response (expecting CONNECTED)
            response = await ws.recv()
            print(f"Handshake Result:\n{response[:200]}...")

            if "CONNECTED" not in response:
                print("Handshake failed to reach CONNECTED state.")
                if "ERROR" in response:
                    print("Server returned an ERROR frame.")
                return

            # Subscribe to soccer live events
            # This was the most active topic in the logs
            topic = "/api/eventgroups/soccer-live-match-events-small"
            await ws.send(subscribe_frame(topic, "sub-0"))
            print(f"Subscribed to {topic}")

            print("Listening for messages (30s)...\n")
            start_time = time.time()

            while time.time() - start_time < 30:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)

                    if msg.startswith("MESSAGE"):
                        parts = msg.split("\n\n", 1)
                        if len(parts) > 1:
                            body = parts[1].rstrip('\x00')
                            try:
                                data = json.loads(body)
                                print(f"[MATCH DATA] Received update at {time.strftime('%H:%M:%S')}")
                                if isinstance(data, list):
                                    print(f"Initial List: {len(data)} items found.")
                                    if data: print(f"Sample: {json.dumps(data[0], indent=2)[:300]}...")
                                else:
                                    print(f"Update: {data.get('type', 'DIFF')} for Entity {data.get('entityId')}")
                                    print(f"Sample: {json.dumps(data, indent=2)[:300]}...")
                                print("-" * 40)
                            except json.JSONDecodeError:
                                print(f"Non-JSON message received: {body[:100]}...")
                except asyncio.TimeoutError:
                    # Send heartbeat if necessary (not implemented here for simplicity)
                    continue

            print("PoC completed.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    asyncio.run(run_poc())