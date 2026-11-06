# Native FNF runner (Wine + noVNC)

This optional service runs a **specific, allowlisted Windows executable** inside Wine and exposes its virtual desktop through noVNC on port `6080`. It is separate from the browser web-build launcher on port `8080`.

This is intended for legally obtained native builds. Do not use it to bypass DRM or access controls. Keep port 6080 private; a public VNC viewer can control the running game.

## Mod catalog

[`mod-catalog.json`](mod-catalog.json) lists verified creator-linked or platform-hosted pages for several popular native FNF mods. It is metadata only: the repository does not redistribute their executable files, and the runner never scrapes pages or auto-runs an arbitrary download. Open a source page, review its license and download, place the chosen executable under `native-runner/games/`, and add that exact container path to `config/allowlist.json`.

## Setup

From the repository root:

```bash
mkdir -p native-runner/games native-runner/config
cp native-runner/allowlist.example.json native-runner/config/allowlist.json
```

## One-time download

If you have a direct, authorized HTTPS ZIP URL, you can download it once into the persistent Codespace workspace instead of uploading it every session. Copy `manifest.example.json` to `manifest.json`, replace the placeholder URL with the direct release-asset URL, and optionally add its SHA-256 checksum:

```bash
cp native-runner/manifest.example.json native-runner/manifest.json
python3 tools/install_native.py --manifest native-runner/manifest.json
```

The script stores the extracted files under `native-runner/games/`. Do not use a GameBanana page URL as the `url`; use a direct download URL only when the host and mod author permit automated downloading. The repository does not scrape GameBanana or redistribute its files.

For catalog entries hosted on GameBanana, the installer can resolve the current official archive automatically:

```bash
python3 tools/install_native.py --list
python3 tools/install_native.py --mod sonic-exe
```

For a source page with multiple archives, choose one by its displayed filename:

```bash
python3 tools/install_native.py --mod sonic-exe --file-name vs_sonicexe_final_build.rar
```

Use `--dry-run` to resolve and show the selected archive without downloading it. The installer verifies the checksum supplied by GameBanana, extracts the archive, and does not launch the executable.

ZIP, RAR, and 7z archives are supported. RAR archives use the full `unrar` extractor first, with `p7zip-full` as a fallback. The native runner image includes both; rebuild it after pulling this update:

```bash
docker compose -f compose.yaml build --no-cache
```

For the host-side installer, use the full RARLAB-compatible package rather than `unrar-free`:

```bash
sudo apt-get update
sudo apt-get install -y unrar
```

Put a game in its own directory, for example:

```text
native-runner/games/indie-cross/game.exe
```

Edit `native-runner/config/allowlist.json` so it contains the absolute container path:

```json
{
  "executables": ["/games/indie-cross/game.exe"]
}
```

Start it:

```bash
cd native-runner
GAME_EXE=/games/indie-cross/game.exe docker compose -f compose.yaml up --build
```

Forward **port 6080** in the Codespaces Ports panel, then open:

```text
https://<forwarded-host>/vnc.html?autoconnect=1&resize=remote
```

Stop it with `Ctrl-C` or `docker compose down`.

## Important limitations

- Wine is not perfect; some FNF builds may fail because of codecs, DirectX features, or missing Windows dependencies.
- This container is not GPU-accelerated.
- Audio and keyboard input are carried through the VNC session and may have latency.
- The runner intentionally refuses executables outside `/games` and executables missing from the allowlist.
- The default Compose port binding is `127.0.0.1:6080`; do not change it to `0.0.0.0` unless you understand the exposure risk.
