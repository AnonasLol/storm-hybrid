import json
import requests
import ssl
from typing import Optional


def send(server_url: str, install_token: str, payload: dict, proxy: Optional[str] = None, timeout: int = 15) -> bool:
    try:
        data = json.dumps(payload, default=str, ensure_ascii=False).encode("utf-8")
        sess = requests.Session()
        sess.verify = False
        if proxy:
            sess.proxies = {"https": proxy, "http": proxy}
        headers = {
            "X-Install-Token": install_token,
            "Content-Type": "application/json",
        }
        r = sess.post(
            f"{server_url.rstrip('/')}/api/collect",
            data=data,
            headers=headers,
            timeout=timeout,
        )
        return r.status_code == 200
    except Exception:
        return False
