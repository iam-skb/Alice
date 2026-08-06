# src/client.py
import asyncio
import websockets
import json
import base64
import os
import sys
from crypto import AliceCrypto

class AliceClient:
    def __init__(self, client_id, uri="ws://127.0.0.1:8765"):
        self.client_id = client_id
        self.uri = uri
        self.crypto = AliceCrypto()
        self.crypto.generate_keypair()
        self.session_keys = {}  # target -> shared key
        self.websocket = None
        self.running = True

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        # Envoyer la clé publique au serveur
        pub = base64.b64encode(self.crypto.get_public_bytes()).decode()
        await self.websocket.send(json.dumps({
            "type": "register",
            "client_id": self.client_id,
            "public_key": pub
        }))
        resp = await self.websocket.recv()
        print(f"[+] {json.loads(resp).get('status', 'ok')}")
        return self

    async def send_message(self, target, plaintext):
        # Échange de clé simplifié (en vrai, on passerait par le serveur)
        # Ici, on génère une clé statique pour l'exemple
        if target not in self.session_keys:
            # Simuler un échange de clé (à remplacer par un vrai échange)
            self.session_keys[target] = os.urandom(32)
        key = self.session_keys[target]
        encrypted = self.crypto.encrypt_aes_gcm(key, plaintext)
        await self.websocket.send(json.dumps({
            "type": "message",
            "target": target,
            "payload": encrypted
        }))

    async def listen(self):
        try:
            async for msg in self.websocket:
                data = json.loads(msg)
                if data.get("type") == "message":
                    from_user = data["from"]
                    key = self.session_keys.get(from_user)
                    if key:
                        try:
                            decrypted = self.crypto.decrypt_aes_gcm(key, data["payload"])
                            print(f"\n[📩 {from_user}] {decrypted}")
                        except:
                            print("[!] Échec de déchiffrement")
                    else:
                        print(f"[!] Pas de clé pour {from_user}, message ignoré")
        except:
            pass

    async def run(self):
        print(f"\n[🔥] Alice Client – {self.client_id}")
        print("[⚡] Tapez /msg [destinataire] [message]")
        print("[⚡] /status pour voir les clés, /exit pour quitter\n")

        asyncio.create_task(self.listen())

        while self.running:
            try:
                cmd = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
                if not cmd:
                    continue
                if cmd.startswith("/msg "):
                    parts = cmd.split(" ", 2)
                    if len(parts) >= 3:
                        await self.send_message(parts[1], parts[2])
                    else:
                        print("[!] Usage: /msg [destinataire] [message]")
                elif cmd == "/status":
                    print(f"[+] Clés de session: {list(self.session_keys.keys())}")
                elif cmd == "/exit":
                    self.running = False
                    break
                else:
                    print("[!] Commande inconnue. Utilisez /msg, /status, /exit")
            except KeyboardInterrupt:
                break

        await self.websocket.close()
        print("[+] Déconnecté")

async def main():
    client_id = input("Identifiant > ")
    client = AliceClient(client_id)
    await client.connect()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
