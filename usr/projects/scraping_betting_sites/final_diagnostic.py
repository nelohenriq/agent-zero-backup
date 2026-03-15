import asyncio
import websockets
import time

def create_frame(command, headers, body=""):
    frame = command + "\n"
    for key, value in headers.items():
        frame += f"{key}:{value}\n"
    frame += "\n" + body + "\x00"
    return frame

async def diag():
    host = "sportswidget.placard.pt"
    url = f"wss://{host}/api/websocket"
    headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.placard.pt"}
    
    try:
        async with websockets.connect(url, additional_headers=headers, subprotocols=["v10.stomp", "v11.stomp", "v12.stomp"]) as ws:
            await ws.send(create_frame("CONNECT", {"host": host, "protocol-version": "1.5", "accept-version": "1.2,1.1,1.0", "heart-beat": "10000,10000"}))
            print("Handshake sent...")
            
            # Subscribe to multiple topics
            topics = ["/api/eventgroups/soccer-live-match-events-small", "/api/eventgroups/soccer-highlights-events-small"]
            for i, t in enumerate(topics):
                await ws.send(create_frame("SUBSCRIBE", {"id": f"sub-{i}", "destination": t}))
                print(f"Subscribed to {t}")

            start = time.time()
            while time.time() - start < 15:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    # Print first 200 chars of any message to verify traffic
                    print(f"RAW RECV: {repr(msg[:200])}")
                except asyncio.TimeoutError:
                    await ws.send("\n")
                    print("Heartbeat sent...")
    except Exception as e:
        print(f"DIAG ERROR: {e}")

asyncio.run(diag())
