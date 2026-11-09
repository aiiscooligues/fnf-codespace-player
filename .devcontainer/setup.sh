#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mkdir -p mods roms/nes roms/snes roms/genesis roms/gb roms/gba roms/psp \
  native-runner/games native-runner/config rom-runner/config
chmod +x start.sh native-runner/entrypoint.sh rom-runner/entrypoint.sh \
  tools/install_mods.py tools/install_native.py 2>/dev/null || true

# Keep setup non-fatal: Codespaces may have unavailable or broken third-party APT sources.
if command -v 7z >/dev/null 2>&1; then
  echo "7z: available"
else
  echo "7z: not installed; RAR/7z downloads can be enabled later with p7zip-full"
fi
if command -v unrar >/dev/null 2>&1; then
  echo "unrar: available"
else
  echo "unrar: not installed; full RAR extraction can be enabled later with unrar"
fi
if command -v docker >/dev/null 2>&1; then
  echo "docker CLI: available"
else
  echo "docker CLI: not available in this Codespace image"
fi

if [[ ! -f native-runner/config/allowlist.json ]]; then
  cp -n native-runner/allowlist.example.json native-runner/config/allowlist.json 2>/dev/null || true
fi

echo "FNF Codespace Player setup complete."
