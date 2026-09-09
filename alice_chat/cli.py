import asyncio
import websockets
import json
import os
import hashlib
import base64
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
RESET = "\033[0m"
BOLD = "\033[1m"

RELAY = "wss://alice-relay.onrender.com"

class AliceCrypto:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keypair(self):
        private = x25519.X25519PrivateKey.generate()
        public = private.public_key()
        self.private_key = private
        self.public_key = public
        return private, public

    def get_public_bytes(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

    def derive_shared_key(self, peer_public_bytes):
        peer_public = x25519.X25519PublicKey.from_public_bytes(peer_public_bytes)
        shared = self.private_key.exchange(peer_public)
        return hashlib.sha256(shared).digest()

    def encrypt_aes_gcm(self, key, plaintext):
        nonce = get_random_bytes(12)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return base64.b64encode(nonce + tag + ciphertext).decode()

    def decrypt_aes_gcm(self, key, data):
        raw = base64.b64decode(data)
        nonce = raw[:12]
        tag = raw[12:28]
        ciphertext = raw[28:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()

class AliceRoom:
    def __init__(self, name, room):
        self.name = name
        self.room = room
        self.crypto = AliceCrypto()
        self.crypto.generate_keypair()
        self.websocket = None
        self.shared_key = None
        self.running = True

    def show_header(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{CYAN}    █████╗ ██╗     ██╗ ██████╗███████╗{RESET}")
        print(f"{CYAN}   ██╔══██╗██║     ██║██╔════╝██╔════╝{RESET}")
        print(f"{CYAN}   ███████║██║     ██║██║     █████╗  {RESET}")
        print(f"{CYAN}   ██╔══██║██║     ██║██║     ██╔══╝  {RESET}")
        print(f"{CYAN}   ██║  ██║███████╗██║╚██████╗███████╗{RESET}")
        print(f"{CYAN}   ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝╚══════╝{RESET}")
        print("-" * 50)
        print(f"  {BOLD}Alice Linux 1.0.0{RESET}  {GREEN}(Room Secure Chat){RESET}")
        print(f"  Utilisateur: {self.name}")
        print(f"  Salon: {self.room}")
        print("-" * 50)
        print("  Commandes: /msg <message>  /clear  /exit")
        print("-" * 50)
        print()

    def log(self, msg, color=RESET):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {color}{msg}{RESET}")

    async def connect(self):
        self.show_header()
        self.log(f"Connexion au salon {self.room}...", CYAN)
        self.websocket = await websockets.connect(f"{RELAY}/{self.room}")
        await self.websocket.send(json.dumps({"type": "join", "name": self.name}))
        self.log("Connecté !", GREEN)
        await self.exchange_keys()
        await self.listen()

    async def exchange_keys(self):
        my_pub = base64.b64encode(self.crypto.get_public_bytes()).decode()
        await self.websocket.send(json.dumps({"type": "pubkey", "key": my_pub}))
        msg = await self.websocket.recv()
        data = json.loads(msg)
        peer_pub = base64.b64decode(data["key"])
        self.shared_key = self.crypto.derive_shared_key(peer_pub)
        self.log("Clé de session établie.", GREEN)

    async def send_message(self, plaintext):
        if not self.shared_key:
            self.log("Pas de clé de session", RED)
            return
        encrypted = self.crypto.encrypt_aes_gcm(self.shared_key, plaintext)
        await self.websocket.send(json.dumps({"type": "msg", "payload": encrypted}))

    async def listen(self):
        try:
            async for msg in self.websocket:
                data = json.loads(msg)
                if data["type"] == "msg":
                    decrypted = self.crypto.decrypt_aes_gcm(self.shared_key, data["payload"])
                    self.log(f"Message reçu : {decrypted}", YELLOW)
                elif data["type"] == "pubkey":
                    pass
        except:
            self.log("Connexion perdue", RED)
            self.running = False

    async def get_input(self):
        while self.running:
            try:
                cmd = input(f"{GREEN}{self.name}@alice ~$ {RESET}").strip()
                if not cmd: continue
                if cmd == "/exit":
                    self.running = False
                    break
                elif cmd == "/clear":
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.show_header()
                elif cmd.startswith("/msg"):
                    parts = cmd.split(maxsplit=1)
                    if len(parts) < 2:
                        self.log("Usage: /msg <message>", RED)
                    else:
                        await self.send_message(parts[1])
                else:
                    self.log("Commande inconnue.", RED)
            except:
                break

    async def run(self):
        await asyncio.gather(self.listen(), self.get_input())

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Alice Room Chat")
    parser.add_argument("--room", required=True, help="Nom du salon")
    args = parser.parse_args()

    name = input("Votre pseudo > ")
    alice = AliceRoom(name, args.room)
    asyncio.run(alice.connect())
    asyncio.run(alice.run())
