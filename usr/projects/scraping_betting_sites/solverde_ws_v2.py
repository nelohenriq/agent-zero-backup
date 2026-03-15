import websocket
import json
import time
import threading

messages = []
connected = False

def on_message(ws, msg):
    global messages
    print(f'>>> {msg[:300]}')
    messages.append({'time': time.time(), 'data': msg})

def on_error(ws, error):
    print(f'ERROR: {error}')

def on_close(ws, close_status_code, close_msg):
    print(f'CLOSED: {close_status_code} - {close_msg}')

def on_open(ws):
    global connected
    connected = True
    print('CONNECTED - sending subscription...')
    # Try different subscription formats
    subs = [
        '{"action":"subscribe","channel":"live-odds"}',
        '{"cmd":"subscribe","channel":"sportsbook"}',
        '{"type":"subscribe","sport":"football"}',
        '{"subscribe":"odds"}',
        'ping'
    ]
    for s in subs:
        print(f'Sending: {s}')
        ws.send(s)
        time.sleep(0.5)

ws_url = "wss://sportswidget.solverde.pt/api/websocket"
print(f'Connecting to {ws_url}...')
ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)

# Run for 10 seconds
ws.run_forever(ping_interval=10, ping_timeout=5)

print(f'\n=== Captured {len(messages)} messages ===')
if messages:
    with open('solverde_ws_direct.json', 'w') as f:
        json.dump(messages, f, indent=2)
    print('Saved to solverde_ws_direct.json')
else:
    print('No messages received - checking if connection worked...')
