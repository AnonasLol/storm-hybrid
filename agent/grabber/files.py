import os
from pathlib import Path

TARGET_DIRS = [
    Path.home() / "Documents",
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    Path.home() / "Pictures",
]


def find_files(extensions: list[str], max_size: int) -> list[dict]:
    results = []
    for base in TARGET_DIRS:
        if not base.exists():
            continue
        try:
            for f in base.rglob("*"):
                if not f.is_file():
                    continue
                if f.suffix.lower() not in extensions:
                    continue
                try:
                    size = f.stat().st_size
                    if size > max_size or size == 0:
                        continue
                    results.append({
                        "path": str(f),
                        "name": f.name,
                        "size": size,
                        "ext": f.suffix.lower(),
                    })
                except Exception:
                    pass
        except Exception:
            pass
    return results
