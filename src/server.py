# src/server.py
import asyncio
import websockets
import json
import logging
import time

logging.basicConfig(level=logging.INFO)

clients = {}  # {client_id: websocket}

async def handler(websocket, path):
    client_id = None
    try:
        async for msg in websocket:
            data = json.loads(msg)
            if data.get("type") == "register":
                client_id = data["client_id"]
                clients[client_id] = websocket
                logging.info(f"[+] {client_id} connecté")
                await websocket.send(json.dumps({"type": "registered", "status": "ok"}))
            elif data.get("type") == "message":
                target = data["target"]
                if target in clients:
                    await clients[target].send(json.dumps({
                        "type": "message",
                        "from": client_id,
                        "payload": data["payload"]
                    }))
                else:
                    await websocket.send(json.dumps({"type": "error", "msg": "Cible hors ligne"}))
    except:
        pass
    finally:
        if client_id and client_id in clients:
            del clients[client_id]
            logging.info(f"[-] {client_id} déconnecté")

print("[🔥] Alice Relay sur ws://0.0.0.0:8765")
asyncio.get_event_loop().run_until_complete(
    websockets.serve(handler, "0.0.0.0", 8765)
)
asyncio.get_event_loop().run_forever()
