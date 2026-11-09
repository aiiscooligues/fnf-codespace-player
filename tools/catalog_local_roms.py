#!/usr/bin/env python3
"""Create roms_catalog.json from ROM files already present under roms/.

This script is intentionally offline: it does not scrape ROM sites, resolve
external download endpoints, or download game files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

EXTENSIONS = {
    ".nes": "NES",
    ".fds": "NES",
    ".sfc": "SNES",
    ".smc": "SNES",
    ".md": "Genesis / Mega Drive",
    ".gen": "Genesis / Mega Drive",
    ".bin": "Genesis / Mega Drive",
    ".gb": "Game Boy",
    ".gbc": "Game Boy Color",
    ".gba": "Game Boy Advance",
    ".iso": "PSP / disc image",
    ".cso": "PSP",
}
DEFAULT_IGNORES = {".zip", ".rar", ".7z", ".chd"}
CHUNK_SIZE = 1024 * 1024


def title_from_path(path: Path) -> str:
    value = path.stem.replace("_", " ").replace("-", " ")
    return re.sub(r"\s+", " ", value).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def platform_for(path: Path) -> str:
    for part in path.parts:
        key = part.lower()
        if key in {"nes", "snes", "genesis", "gb", "gba", "psp"}:
            return {"nes": "NES", "snes": "SNES", "genesis": "Genesis / Mega Drive", "gb": "Game Boy", "gba": "Game Boy Advance", "psp": "PSP"}[key]
    return EXTENSIONS.get(path.suffix.lower(), "Unknown")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roms-dir", type=Path, default=Path("roms"))
    parser.add_argument("--output", type=Path, default=Path("roms_catalog.json"))
    parser.add_argument("--include-archives", action="store_true", help="include ZIP/RAR/7z/CHD files as entries")
    args = parser.parse_args()

    root = args.roms_dir.resolve()
    if not root.exists():
        raise SystemExit(f"ROM directory does not exist: {root}")

    allowed = set(EXTENSIONS)
    if args.include_archives:
        allowed |= DEFAULT_IGNORES

    entries = []
    for path in sorted(root.rglob("*"), key=lambda p: str(p).lower()):
        if not path.is_file() or path.suffix.lower() not in allowed:
            continue
        relative = path.relative_to(root).as_posix()
        entries.append({
            "title": title_from_path(path),
            "platform": platform_for(path),
            "filename": path.name,
            "relative_path": f"{args.roms_dir.as_posix().rstrip('/')}/{relative}",
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    output = {
        "generated_by": "tools/catalog_local_roms.py",
        "source": "local roms/ directory",
        "online_lookup": False,
        "games": entries,
    }
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Cataloged {len(entries)} local ROM file(s) into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
