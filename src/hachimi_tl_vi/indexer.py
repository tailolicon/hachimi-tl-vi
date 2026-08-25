from __future__ import annotations

import json
from pathlib import Path

try:
    from blake3 import blake3 as _native_blake3
except ImportError:
    _native_blake3 = None

from .blake3_pure import blake3_hex as _pure_blake3_hex


def _hash(data: bytes) -> str:
    if _native_blake3 is not None:
        return _native_blake3(data).hexdigest()
    return _pure_blake3_hex(data)


def generate_index(
    localized_dir: str | Path = "localized_data",
    index_base: str | Path = "index_base.json",
    output: str | Path = "index.json",
) -> dict:
    localized_dir = Path(localized_dir)
    index = json.loads(Path(index_base).read_text(encoding="utf-8"))
    files = []
    for path in sorted(p for p in localized_dir.rglob("*") if p.is_file() and p.name not in {".gitignore", ".gitkeep"}):
        data = path.read_bytes()
        files.append({
            "path": path.relative_to(localized_dir).as_posix(),
            "hash": _hash(data),
            "size": len(data),
        })
    index["files"] = files
    Path(output).write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return index
