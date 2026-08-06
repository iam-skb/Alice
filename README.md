markdown

# ALICE – Secure Encrypted Chat



| Version | Langage | Chiffrement | Statut |
| :--- | :--- | :--- | :--- |
| 1.0.0 | Python 3 | X25519 + AES‑256‑GCM (E2EE) | Prêt à l’emploi |

---

## 📖 Description

Alice est un outil de messagerie instantanée chiffrée de bout en bout (E2EE) en ligne de commande.  
Il repose sur un **échange de clé X25519** (Diffie‑Hellman) et un **chiffrement AES‑256‑GCM** pour garantir la confidentialité des messages et des fichiers échangés.

Le serveur central ne fait que relayer les données chiffrées : **il ne peut pas lire le contenu des messages**.

---

## ⚙️ Fonctionnalités

| Fonctionnalité | Description |
| :--- | :--- |
| **Chiffrement E2EE** | Échange de clé X25519 + AES‑256‑GCM |
| **Messages et fichiers** | Tous les échanges sont chiffrés |
| **Interface terminal** | Logo, couleurs, commandes slash |
| **Multi‑clients** | Plusieurs utilisateurs en simultané |
| **Historique chiffré** | Logs locaux chiffrés sur le disque |
| **Reconnexion auto** | Reconnexion automatique si le serveur tombe |
| **Affichage non bloquant** | Les messages n’interrompent pas la saisie |

---

## 🧠 Architecture

Client A ←── chiffré E2EE ──► Relais Alice ◄── chiffré E2EE ──► Client B
text


| Composant | Rôle |
| :--- | :--- |
| **Relais (`server.py`)** | WebSocket, ne stocke rien, ne déchiffre rien |
| **Client (`client.py`)** | Génère les clés, chiffre, déchiffre |

---

## 📦 Installation

### Prérequis

- Python ≥ 3.8
- `pip` (gestionnaire de paquets)

### 1. Cloner le dépôt

```bash
git clone https://github.com/theanonspider/Alice.git
cd Alice

2. Créer un environnement virtuel (recommandé)
bash

python3 -m venv alice_env
source alice_env/bin/activate  # Linux/macOS
# alice_env\Scripts\activate    # Windows

3. Installer les dépendances
bash

pip install -r requirements.txt

🚀 Utilisation
Démarrer le serveur (relais)
bash

python3 src/server.py

👉 Le serveur écoute sur ws://0.0.0.0:8766.
Démarrer un client (dans un autre terminal)
bash

python3 src/client.py

👉 Saisissez un identifiant (ex: alice).
Démarrer un deuxième client
bash

python3 src/client.py

👉 Saisissez un autre identifiant (ex: bob).
Envoyer un message
text

/msg bob "Salut Bob, ce message est chiffré !"

⌨️ Commandes disponibles
Commande	Effet
/msg <user> <message>	Envoyer un message chiffré
/file <user> <path>	Envoyer un fichier chiffré
/status	Afficher le nombre de sessions actives
/clear	Effacer l’écran
/help	Afficher la liste des commandes
/exit	Quitter proprement
🔒 Sécurité
Mécanisme	Détail
Échange de clé	X25519 (ECDH) – chaque session a sa propre clé
Chiffrement	AES‑256‑GCM (authentifié)
Confidentialité	Le serveur ne voit que du base64 chiffré
Historique	Chiffré avec une clé dérivée de l’identifiant
📁 Structure

---
Alice/
├── src/
│   ├── crypto.py       # X25519 + AES‑256‑GCM
│   ├── server.py       # Relais WebSocket
│   └── client.py       # Interface terminal
├── README.md
└── requirements.txt
---

👤 Auteur
TheAnonSpider
GitHub : https://github.com/theanonspider
---
⚠️ Avertissement
Usage éducatif et de recherche uniquement.
Toute utilisation non autorisée est illégale.
---
📝 Licence
MIT – pour un usage éducatif et open‑source.
