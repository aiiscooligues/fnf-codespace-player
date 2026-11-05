#!/usr/bin/env python3
"""Download and install explicitly listed FNF web builds into mods/.

The manifest is intentionally user-maintained. This script does not scrape sites
or guess download URLs, and it only accepts ZIP archives over HTTPS by default.
"""
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
DEFAULT_MANIFEST = ROOT / "mods" / "manifest.json"
DEFAULT_MODS = ROOT / "mods"
MAX_DOWNLOAD_BYTES = 2 * 1024 * 1024 * 1024  # 2 GiB safety limit


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip(".-")
    if not value or value in {".", ".."}:
        raise ValueError("name must contain at least one safe filename character")
    return value[:80]


def download(url: str, destination: Path) -> str:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-HTTPS URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "fnf-codespace-player/1.0"})
    digest = hashlib.sha256()
    total = 0
    with urllib.request.urlopen(request, timeout=60) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                raise ValueError("download exceeds the 2 GiB safety limit")
            digest.update(chunk)
            output.write(chunk)
    return digest.hexdigest()


def safe_zip_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = Path(member.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe ZIP path: {member.filename}")
        if member.filename.startswith(("/", "\\")):
            raise ValueError(f"unsafe ZIP path: {member.filename}")


def find_build_root(extracted: Path) -> Path:
    candidates = [path.parent for path in extracted.rglob("index.html") if path.is_file()]
    unique = sorted(set(candidates), key=lambda path: (len(path.parts), str(path)))
    if not unique:
        raise ValueError("archive does not contain an index.html web entry point")
    if len(unique) > 1:
        top_level = [path for path in unique if path.parent == extracted]
        if len(top_level) == 1:
            return top_level[0]
        raise ValueError("archive contains multiple index.html files; install it manually")
    return unique[0]


def install_item(item: dict, mods_dir: Path, force: bool) -> None:
    if not isinstance(item, dict):
        raise ValueError("each manifest item must be an object")
    name = item.get("name")
    url = item.get("url")
    expected_sha = item.get("sha256")
    if not isinstance(name, str) or not isinstance(url, str):
        raise ValueError("each item needs string fields: name and url")
    slug = slugify(name)
    if expected_sha is not None and (not isinstance(expected_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha)):
        raise ValueError("sha256 must be a 64-character hexadecimal checksum")

    destination = mods_dir / slug
    if destination.exists() and not force:
        raise FileExistsError(f"{destination} already exists; rerun with --force to replace it")

    with tempfile.TemporaryDirectory(prefix="fnf-mod-") as temp_dir:
        temp = Path(temp_dir)
        archive_path = temp / "download.zip"
        print(f"Downloading {name}…")
        actual_sha = download(url, archive_path)
        if expected_sha and actual_sha.lower() != expected_sha.lower():
            raise ValueError(f"SHA-256 mismatch for {name}: expected {expected_sha}, got {actual_sha}")
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"ZIP integrity check failed for {name}")
            safe_zip_members(archive)
            extracted = temp / "extracted"
            archive.extractall(extracted)
        build_root = find_build_root(extracted)
        staged = temp / "staged"
        shutil.copytree(build_root, staged)
        if destination.exists():
            shutil.rmtree(destination)
        staged.rename(destination)
    print(f"Installed {name} at {destination.relative_to(ROOT)} (sha256: {actual_sha})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--mods-dir", type=Path, default=DEFAULT_MODS)
    parser.add_argument("--force", action="store_true", help="replace existing mod folders")
    parser.add_argument("--dry-run", action="store_true", help="validate the manifest without downloading")
    args = parser.parse_args()

    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("manifest root must be a JSON array")
        for item in data:
            if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not isinstance(item.get("url"), str):
                raise ValueError("every manifest item needs name and url")
            slugify(item["name"])
            if not args.dry_run:
                args.mods_dir.mkdir(parents=True, exist_ok=True)
                install_item(item, args.mods_dir, args.force)
            else:
                print(f"OK: {item['name']} -> {slugify(item['name'])}")
    except (OSError, ValueError, KeyError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
