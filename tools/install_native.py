#!/usr/bin/env python3
"""Install an explicitly authorized native mod archive into native-runner/games."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "native-runner" / "manifest.json"
DEFAULT_GAMES = ROOT / "native-runner" / "games"
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024 * 1024


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip(".-")
    if not slug or slug in {".", ".."}:
        raise ValueError("name must contain a safe filename")
    return slug[:80]


def download(url: str, destination: Path) -> str:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-HTTPS URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "fnf-codespace-player/1.0"})
    digest = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                raise ValueError("download exceeds the 3 GiB safety limit")
            digest.update(chunk)
            output.write(chunk)
    return digest.hexdigest()


def safe_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = Path(member.filename)
        if path.is_absolute() or ".." in path.parts or member.filename.startswith(("/", "\\")):
            raise ValueError(f"unsafe ZIP path: {member.filename}")


def find_executables(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.exe") if path.is_file())


def install(item: dict, games_dir: Path, force: bool) -> None:
    name = item.get("name")
    url = item.get("url")
    checksum = item.get("sha256")
    if not isinstance(name, str) or not isinstance(url, str):
        raise ValueError("each item needs string fields: name and url")
    if checksum is not None and (not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", checksum)):
        raise ValueError("sha256 must be 64 hexadecimal characters")
    slug = slugify(name)
    destination = games_dir / slug
    if destination.exists() and not force:
        raise FileExistsError(f"{destination} already exists; use --force to replace it")

    with tempfile.TemporaryDirectory(prefix="fnf-native-") as temp_dir:
        temp = Path(temp_dir)
        archive_path = temp / "download.zip"
        print(f"Downloading {name}…")
        actual = download(url, archive_path)
        if checksum and actual.lower() != checksum.lower():
            raise ValueError(f"SHA-256 mismatch: expected {checksum}, got {actual}")
        extracted = temp / "extracted"
        with zipfile.ZipFile(archive_path) as archive:
            safe_members(archive)
            archive.extractall(extracted)
        executables = find_executables(extracted)
        if not executables:
            raise ValueError("archive contains no .exe file")
        root = temp / "staged"
        root.mkdir()
        for child in extracted.iterdir():
            target = root / child.name
            if child.is_dir():
                shutil.copytree(child, target)
            else:
                shutil.copy2(child, target)
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        root.rename(destination)
        installed = [path.relative_to(extracted) for path in executables]
    print(f"Installed {name} in {destination}")
    print("Executables found:")
    for path in installed:
        print(f"  {destination / path}")
    print(f"sha256: {actual}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--games-dir", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("manifest root must be a JSON array")
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("each manifest item must be an object")
            args.games_dir.mkdir(parents=True, exist_ok=True)
            install(item, args.games_dir, args.force)
    except (OSError, ValueError, KeyError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
