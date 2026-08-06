# src/crypto.py
import os
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import HKDF
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

class AliceCrypto:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.session_keys = {}

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
        return HKDF(master=shared, key_len=32, salt=None, hashmod=hashlib.sha256)

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
