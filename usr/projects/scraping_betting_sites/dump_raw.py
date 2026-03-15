import asyncio
import websockets
import json
import os

def create_frame(command, headers, body=""):
    frame = command + "\n"
    for key, value in headers.items():
        frame += f"{key}:{value}\n"
    frame += "\n" + body + "\x00"
    return frame

async def dump():
    host = "sportswidget.placard.pt"
    url = f"wss://{host}/api/websocket"
    topic = "/api/eventgroups/soccer-live-match-events-small"
    
    headers = {"User-Agent": "Mozilla/5.0", "Origin": "https://www.placard.pt"}

    try:
        async with websockets.connect(url, additional_headers=headers, subprotocols=["v10.stomp", "v11.stomp", "v12.stomp"]) as ws:
            await ws.send(create_frame("CONNECT", {"host": host, "protocol-version": "1.5", "accept-version": "1.2,1.1,1.0", "heart-beat": "10000,10000"}))
            while True:
                msg = await ws.recv()
                if "CONNECTED" in msg: break
            
            await ws.send(create_frame("SUBSCRIBE", {"id": "sub-dump", "destination": topic}))
            
            while True:
                msg = await ws.recv()
                if msg == "\n": continue
                if "MESSAGE" in msg:
                    body = msg.split("\n\n", 1)[1].split("\x00", 1)[0]
                    with open("/a0/usr/projects/scraping_betting_sites/raw_sample.json", "w") as f:
                        f.write(body)
                    print("Raw data saved to raw_sample.json")
                    return
    except Exception as e:
        print(f"Dump error: {e}")

if __name__ == "__main__":
    asyncio.run(dump())
