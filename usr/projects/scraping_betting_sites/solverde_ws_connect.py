import websocket
import json
import time

print('Connecting to Solverde WebSocket...')
ws_url = "wss://sportswidget.solverde.pt/api/websocket"

messages = []

def on_message(ws, msg):
    print(f'Received: {msg[:200]}...')
    messages.append({'time': time.time(), 'data': msg})
    if len(messages) >= 50:
        ws.close()

def on_error(ws, error):
    print(f'Error: {error}')

def on_close(ws, close_status_code, close_msg):
    print(f'Closed: {close_status_code} - {close_msg}')

def on_open(ws):
    print('WebSocket opened!')
    ws.send('{"type":"subscribe","channel":"sports"}')

try:
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever(ping_interval=30)
except Exception as e:
    print(f'Connection error: {e}')

print(f'Captured {len(messages)} messages')
with open('solverde_ws_direct.json', 'w') as f:
    json.dump(messages, f, indent=2)
print('Saved to solverde_ws_direct.json')
