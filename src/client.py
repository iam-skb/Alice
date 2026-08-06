import asyncio
import websockets
import json
import os
import sys
import time
import random
from datetime import datetime
from crypto import AliceCrypto

# Couleurs exactes du terminal Fedora
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
RESET = "\033[0m"
BOLD = "\033[1m"
GRAY = "\033[0;37m"
WHITE = "\033[1;37m"

class AliceClient:
    def __init__(self, client_id, uri="ws://127.0.0.1:8765"):
        self.client_id = client_id
        self.uri = uri
        self.crypto = AliceCrypto()
        self.crypto.generate_keypair()
        self.websocket = None
        self.targets = {}
        self.running = True
        self.history = []
        self.fedora_version = "44 (Workstation Edition)"
        self.kernel = "6.8.5-301.fc44.x86_64"
        self.uptime = "14:29:08 up 1 day, 3:42, 4 users, load average: 0.1, 0.2, 0.1"

    def log(self, msg, color=GREEN, prefix="[LOG]"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"{GRAY}{timestamp}{RESET} {color}{msg}{RESET}"
        self.history.append(line)
        print(line)

    async def connect(self):
        self.log(f"Connexion au relais Alice...", CYAN)
        try:
            self.websocket = await websockets.connect(self.uri)
            await self.websocket.send(json.dumps({
                "type": "register",
                "client_id": self.client_id
            }))
            resp = await self.websocket.recv()
            self.log(f"✅ {json.loads(resp)['status']}", GREEN)
            return True
        except Exception as e:
            self.log(f"❌ Erreur de connexion : {e}", RED)
            return False

    async def send(self, target, plaintext):
        if target not in self.targets:
            self.targets[target] = self.crypto.derive_shared_key(os.urandom(32))
        key = self.targets[target]
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
                if data["type"] == "message":
                    from_user = data["from"]
                    key = self.targets.get(from_user)
                    if key:
                        try:
                            decrypted = self.crypto.decrypt_aes_gcm(key, data["payload"])
                            self.log(f"📩 {from_user}: {decrypted}", YELLOW)
                        except:
                            self.log(f"❌ Échec de déchiffrement de {from_user}", RED)
        except:
            self.running = False

    def show_header(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        # Style exact de l'écran Fedora
        print(f"{BOLD}{WHITE}┌──────────────────────────────────────────────────────────────┐{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{CYAN}█████████╗ ██╗     ██╗ ██████╗███████╗{WHITE}                   │{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{CYAN}██╔════╝ ██║     ██║██╔════╝██╔════╝{WHITE}                   │{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{CYAN}█████╗   ██║     ██║██║     █████╗  {WHITE}                   │{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{CYAN}██╔══╝   ██║     ██║██║     ██╔══╝  {WHITE}                   │{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{CYAN}██║      ███████╗██║╚██████╗███████╗{WHITE}                   │{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{CYAN}╚═╝      ╚══════╝╚═╝ ╚═════╝╚══════╝{WHITE}                   │{RESET}")
        print(f"{BOLD}{WHITE}├──────────────────────────────────────────────────────────────┤{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BOLD}{GREEN}Alice Linux{RESET} {BOLD}{WHITE}1.0.0{RESET} {GRAY}(Dieu du Chat){RESET}                         {WHITE}│{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BLUE}Utilisateur:{RESET} {BOLD}{YELLOW}{self.client_id}{RESET}                                     {WHITE}│{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{BLUE}Relais:{RESET} {self.uri}{RESET}                               {WHITE}│{RESET}")
        print(f"{BOLD}{WHITE}├──────────────────────────────────────────────────────────────┤{RESET}")
        print(f"{BOLD}{WHITE}│  {RESET}{GRAY}Commandes :{RESET} {YELLOW}/msg [user] [msg]  /status  /exit{RESET}              {WHITE}│{RESET}")
        print(f"{BOLD}{WHITE}└──────────────────────────────────────────────────────────────┘{RESET}")
        print()

    def show_prompt(self):
        return f"{GREEN}{self.client_id}@{RESET}{BLUE}alice{RESET} {GRAY}~${RESET} "

    async def run(self):
        self.show_header()
        self.log(f"🔑 Clé publique: {self.crypto.get_public_bytes().hex()[:20]}...", CYAN)
        self.log(f"🐧 Fedora Linux {self.fedora_version}", GRAY)
        self.log(f"📦 Noyau {self.kernel}", GRAY)
        self.log(f"⏱️  {self.uptime}", GRAY)

        if not await self.connect():
            return

        asyncio.create_task(self.listen())

        while self.running:
            try:
                cmd = input(self.show_prompt()).strip()
                if not cmd:
                    continue

                if cmd == "/exit":
                    self.running = False
                    break
                elif cmd == "/status":
                    self.log(f"🔐 Sessions actives: {len(self.targets)}", CYAN)
                    self.log(f"📋 Historique: {len(self.history)} messages", GRAY)
                elif cmd.startswith("/msg"):
                    parts = cmd.split(maxsplit=2)
                    if len(parts) < 3:
                        self.log("❌ Usage: /msg [user] [message]", RED)
                    else:
                        await self.send(parts[1], parts[2])
                else:
                    self.log(f"❌ Commande inconnue: {cmd}", RED)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"❌ Erreur: {e}", RED)

        self.log("👋 Déconnexion propre...", CYAN)
        await self.websocket.close()

async def main():
    print(f"{BOLD}{GREEN}┌─────────────────────────────────────┐{RESET}")
    print(f"{BOLD}{GREEN}│  🔥 ALICE – CHAT CHIFFRÉ ULTIME    │{RESET}")
    print(f"{BOLD}{GREEN}└─────────────────────────────────────┘{RESET}")
    client_id = input(f"{GREEN}Identifiant{RESET} > ")
    client = AliceClient(client_id)
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())
