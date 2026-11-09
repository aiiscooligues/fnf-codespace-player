#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

core_for() {
  case "${1,,}" in
    *.nes|*.fds) echo nestopia ;;
    *.sfc|*.smc) echo snes9x ;;
    *.md|*.gen|*.bin) echo genesis_plus_gx ;;
    *.gb) echo gambatte ;;
    *.gbc) echo gambatte ;;
    *.gba) echo mgba ;;
    *.iso|*.cso) echo ppsspp ;;
    *) return 1 ;;
  esac
}

require_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not available in this Codespace. Rebuild the Codespace or use a VM with Docker support."
    exit 1
  fi
  if ! docker info >/dev/null 2>&1; then
    echo "Docker is installed but the daemon is not running. Start Docker, then try again."
    exit 1
  fi
}

play_rom() {
  require_docker
  mapfile -t roms < <(find "$ROOT/roms" -type f \( \
    -iname '*.nes' -o -iname '*.fds' -o -iname '*.sfc' -o -iname '*.smc' \
    -o -iname '*.md' -o -iname '*.gen' -o -iname '*.bin' -o -iname '*.gb' \
    -o -iname '*.gbc' -o -iname '*.gba' -o -iname '*.iso' -o -iname '*.cso' \
  \) -print | sort -f)
  if (( ${#roms[@]} == 0 )); then
    echo "No supported ROMs found in roms/."
    exit 1
  fi

  echo
  echo "Choose a local ROM:"
  local i
  for i in "${!roms[@]}"; do
    printf '  %d) %s\n' "$((i + 1))" "${roms[$i]#"$ROOT/"}"
  done
  echo
  read -r -p "Enter a number: " choice
  if ! [[ "$choice" =~ ^[0-9]+$ ]] || (( choice < 1 || choice > ${#roms[@]} )); then
    echo "Invalid selection."
    exit 1
  fi

  local selected="${roms[$((choice - 1))]}"
  local relative="${selected#"$ROOT/roms/"}"
  local core
  core=$(core_for "$selected") || { echo "No emulator core mapped for this file."; exit 1; }
  echo "Starting $(basename "$selected") with $core on port 6090..."
  cd "$ROOT/rom-runner"
  ROM_PATH="/roms/$relative" CORE="$core" docker compose up --build
}

case "${1:-}" in
  web)
    exec "$ROOT/start.sh"
    ;;
  rom)
    play_rom
    ;;
  "")
    echo "FNF Codespace Player"
    echo
    echo "1) Start web FNF player (port 8080)"
    echo "2) Play a local ROM (port 6090)"
    echo "3) Exit"
    echo
    read -r -p "Choose an option: " option
    case "$option" in
      1) exec "$ROOT/start.sh" ;;
      2) play_rom ;;
      3) exit 0 ;;
      *) echo "Invalid option."; exit 1 ;;
    esac
    ;;
  *)
    echo "Usage: $0 [web|rom]"
    exit 2
    ;;
esac
