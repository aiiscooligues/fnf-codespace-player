#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! curl -fsS http://127.0.0.1:8080/api/mods >/dev/null 2>&1; then
  echo "Starting FNF web launcher on port 8080..."
  nohup "$ROOT/start.sh" >/tmp/fnf-player.log 2>&1 &
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker CLI unavailable; native/ROM container runners are not started."
  exit 0
fi

if docker info >/dev/null 2>&1; then
  echo "Docker daemon already running."
  exit 0
fi

if command -v dockerd >/dev/null 2>&1; then
  echo "Starting Docker daemon..."
  sudo dockerd >/tmp/dockerd.log 2>&1 &
  for _ in $(seq 1 15); do
    sleep 1
    if docker info >/dev/null 2>&1; then
      echo "Docker daemon ready."
      exit 0
    fi
  done
  echo "Docker daemon did not become ready; see /tmp/dockerd.log"
else
  echo "Docker daemon unavailable; use a Codespace/VM with Docker support for native and ROM runners."
fi
exit 0
