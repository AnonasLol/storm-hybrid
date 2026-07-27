import json
import base64
import os
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class Decryptor:
    def __init__(self):
        self._keys: dict[str, bytes] = {}
        self._keys_file = Path(__file__).parent / "server_keys.json"
        self._load()

    def _load(self):
        if self._keys_file.exists():
            try:
                data = json.loads(self._keys_file.read_text())
                for token, key in data.items():
                    self._keys[token] = key.encode()
            except Exception:
                pass

    def _save(self):
        data = {k: v.decode() for k, v in self._keys.items()}
        self._keys_file.write_text(json.dumps(data, indent=2))

    def register_key(self, install_token: str, aes_key: str):
        self._keys[install_token] = aes_key.encode()
        self._save()

    def decrypt(self, b64_data: str, install_token: str = "") -> dict:
        try:
            raw = base64.b64decode(b64_data)
            raw_key = self._keys.get(install_token, b"")
            if not raw_key:
                master = os.environ.get("STORM_MASTER_KEY", "").encode()
                if master:
                    raw_key = master
            if not raw_key:
                return {"error": "no AES key for token", "raw": b64_data[:200]}
            key = hashlib.sha256(raw_key).digest()
            iv, ct = raw[:16], raw[16:]
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            dec = cipher.decryptor()
            padded = dec.update(ct) + dec.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded) + unpadder.finalize()
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            return {"error": str(e), "raw": b64_data[:200]}
