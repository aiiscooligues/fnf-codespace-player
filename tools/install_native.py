#!/usr/bin/env python3
"""Install explicitly selected native FNF mods from creator-linked sources.

GameBanana catalog entries are resolved through its public file metadata endpoint,
so users do not need to find a direct URL. The script never scrapes arbitrary
pages, auto-runs a downloaded executable, or bypasses access controls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "native-runner" / "manifest.json"
DEFAULT_CATALOG = ROOT / "native-runner" / "mod-catalog.json"
DEFAULT_GAMES = ROOT / "native-runner" / "games"
MAX_DOWNLOAD_BYTES = 3 * 1024 * 1024 * 1024
ARCHIVE_EXTENSIONS = {".zip", ".7z", ".rar"}


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip(".-")
    if not slug or slug in {".", ".."}:
        raise ValueError("name must contain a safe filename")
    return slug[:80]


def download(url: str, destination: Path) -> tuple[str, str]:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-HTTPS URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "fnf-codespace-player/1.0"})
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    total = 0
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > MAX_DOWNLOAD_BYTES:
                raise ValueError("download exceeds the 3 GiB safety limit")
            sha256.update(chunk)
            md5.update(chunk)
            output.write(chunk)
    return sha256.hexdigest(), md5.hexdigest()


def safe_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = Path(member.filename)
        if path.is_absolute() or ".." in path.parts or member.filename.startswith(("/", "\\")):
            raise ValueError(f"unsafe ZIP path: {member.filename}")


def extract_archive(archive_path: Path, extracted: Path) -> None:
    extracted.mkdir(parents=True)
    if archive_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(archive_path) as archive:
            safe_members(archive)
            archive.extractall(extracted)
        return
    seven_zip = shutil.which("7z") or shutil.which("7zz")
    if not seven_zip and os.name == "posix" and shutil.which("sudo") and shutil.which("apt-get"):
        print("7z is missing; installing p7zip-full…")
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "p7zip-full"], check=True)
        seven_zip = shutil.which("7z") or shutil.which("7zz")
    if not seven_zip:
        raise RuntimeError("RAR/7z extraction needs p7zip-full; run: sudo apt-get update && sudo apt-get install -y p7zip-full")
    listing = subprocess.run([seven_zip, "l", "-slt", str(archive_path)], check=True, capture_output=True, text=True)
    for line in listing.stdout.splitlines():
        if line.startswith("Path = "):
            member = line.removeprefix("Path = ").strip().replace("\\", "/")
            if member.startswith("/") or "/../" in f"/{member}/" or member.startswith("../") or member == "..":
                raise ValueError(f"unsafe archive path: {member}")
    subprocess.run([seven_zip, "x", "-y", f"-o{extracted}", str(archive_path)], check=True)


def find_executables(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.exe") if path.is_file())


def resolve_gamebanana(item: dict, file_name: str | None) -> dict:
    match = re.search(r"/mods/(?:download/)?(\d+)", item.get("source_url", ""))
    if not match:
        raise ValueError(f"no GameBanana mod ID in source URL for {item.get('name')}")
    mod_id = match.group(1)
    api_url = f"https://gamebanana.com/apiv11/Mod/{mod_id}/DownloadPage"
    request = urllib.request.Request(api_url, headers={"User-Agent": "fnf-codespace-player/1.0", "Accept": "application/json"})
    data = json.load(urllib.request.urlopen(request, timeout=60))
    files = [entry for entry in data.get("_aFiles", []) if Path(entry.get("_sFile", "")).suffix.lower() in ARCHIVE_EXTENSIONS]
    if file_name:
        files = [entry for entry in files if entry.get("_sFile") == file_name]
    if not files:
        raise ValueError(f"no matching downloadable archive found for {item.get('name')}")
    selected = files[0]
    return {**item, "url": selected["_sDownloadUrl"], "archive_name": selected["_sFile"], "md5": selected.get("_sMd5Checksum")}


def resolve_item(item: dict, file_name: str | None) -> dict:
    source = item.get("source_url", "")
    if "gamebanana.com/mods/" in source:
        return resolve_gamebanana(item, file_name)
    if item.get("url"):
        return item
    raise ValueError(f"{item.get('name')} has no automatic public file resolver; use a manifest with a direct authorized URL")


def install(item: dict, games_dir: Path, force: bool, dry_run: bool, file_name: str | None) -> None:
    resolved = resolve_item(item, file_name)
    name = resolved.get("name")
    url = resolved.get("url")
    checksum = resolved.get("sha256")
    expected_md5 = resolved.get("md5")
    if not isinstance(name, str) or not isinstance(url, str):
        raise ValueError("each item needs string fields: name and url")
    if checksum is not None and (not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", checksum)):
        raise ValueError("sha256 must be 64 hexadecimal characters")
    slug = slugify(name)
    destination = games_dir / slug
    if destination.exists() and not force:
        raise FileExistsError(f"{destination} already exists; use --force to replace it")
    print(f"Source: {resolved.get('source_url', url)}")
    print(f"Archive: {resolved.get('archive_name', url.rsplit('/', 1)[-1])}")
    if dry_run:
        return

    with tempfile.TemporaryDirectory(prefix="fnf-native-") as temp_dir:
        temp = Path(temp_dir)
        archive_path = temp / (resolved.get("archive_name") or "download.zip")
        print(f"Downloading {name}…")
        actual_sha, actual_md5 = download(url, archive_path)
        if checksum and actual_sha.lower() != checksum.lower():
            raise ValueError(f"SHA-256 mismatch: expected {checksum}, got {actual_sha}")
        if expected_md5 and actual_md5.lower() != expected_md5.lower():
            raise ValueError(f"MD5 mismatch: expected {expected_md5}, got {actual_md5}")
        extracted = temp / "extracted"
        extract_archive(archive_path, extracted)
        executables = find_executables(extracted)
        if not executables:
            raise ValueError("archive contains no .exe file")
        staged = temp / "staged"
        staged.mkdir()
        for child in extracted.iterdir():
            target = staged / child.name
            if child.is_dir():
                shutil.copytree(child, target)
            else:
                shutil.copy2(child, target)
        if destination.exists():
            shutil.rmtree(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        staged.rename(destination)
        installed = [path.relative_to(extracted) for path in executables]
    print(f"Installed {name} in {destination}")
    print("Executables found:")
    for path in installed:
        print(f"  {destination / path}")
    print(f"sha256: {actual_sha}")


def load_items(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("manifest/catalog root must be a JSON array")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mod", help="catalog ID, for example sonic-exe")
    parser.add_argument("--list", action="store_true", help="list catalog IDs")
    parser.add_argument("--file-name", help="choose a specific archive when a source lists several")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--games-dir", type=Path, default=DEFAULT_GAMES)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        catalog = load_items(args.catalog)
        if args.list:
            for item in catalog:
                print(f"{item.get('id')}: {item.get('name')}")
            return 0
        if args.mod:
            item = next((entry for entry in catalog if entry.get("id") == args.mod), None)
            if not item:
                raise ValueError(f"unknown catalog ID: {args.mod}; run --list")
            install(item, args.games_dir, args.force, args.dry_run, args.file_name)
            return 0
        if not args.manifest.exists():
            raise ValueError(f"manifest not found: {args.manifest}; use --mod or create it from manifest.example.json")
        for item in load_items(args.manifest):
            args.games_dir.mkdir(parents=True, exist_ok=True)
            install(item, args.games_dir, args.force, args.dry_run, args.file_name)
    except (OSError, ValueError, KeyError, RuntimeError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
