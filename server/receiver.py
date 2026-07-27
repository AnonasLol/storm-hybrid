import json
from pathlib import Path


class Receiver:
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self._clients: dict = {}
        self._load()

    def _load(self):
        idx = self.data_dir / "index.json"
        if idx.exists():
            with open(idx) as f:
                self._clients = json.load(f)

    def _save(self):
        idx = self.data_dir / "index.json"
        with open(idx, "w") as f:
            json.dump(self._clients, f, indent=2, default=str)

    def store(self, record: dict):
        token = record["install_token"]
        if token not in self._clients:
            self._clients[token] = {"first_seen": record["timestamp"], "records": []}
        self._clients[token]["last_seen"] = record["timestamp"]
        self._clients[token]["system"] = record.get("system", {})
        self._clients[token]["records"].append(record["id"])

        dump = self.data_dir / f"{record['id']}.json"
        with open(dump, "w") as f:
            json.dump(record, f, indent=2, default=str)

        self._save()

    def list_clients(self) -> list:
        return [{"install_token": k, "first_seen": v.get("first_seen"), "last_seen": v.get("last_seen"), "record_count": len(v.get("records", []))} for k, v in self._clients.items()]

    def get_client(self, token: str) -> dict:
        return self._clients.get(token, {})
