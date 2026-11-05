#!/usr/bin/env bash
set -Eeuo pipefail

: "${DISPLAY:=:99}"
: "${GAME_EXE:=}"
: "${WINEPREFIX:=/wine}"
ALLOWLIST=/config/allowlist.json

if [[ -z "$GAME_EXE" ]]; then
  echo "Set GAME_EXE to an executable path under /games, for example /games/my-mod/game.exe." >&2
  exit 2
fi
if [[ ! -f "$ALLOWLIST" ]]; then
  echo "Missing $ALLOWLIST. Copy allowlist.example.json and explicitly authorize the executable." >&2
  exit 2
fi

resolved_game=$(realpath -e -- "$GAME_EXE")
resolved_games=$(realpath -e /games)
case "$resolved_game" in
  "$resolved_games"/*) ;;
  *) echo "Refusing executable outside /games: $GAME_EXE" >&2; exit 3 ;;
esac

python3 - "$ALLOWLIST" "$resolved_game" <<'PY'
import json, pathlib, sys
allowlist = pathlib.Path(sys.argv[1])
exe = pathlib.Path(sys.argv[2]).resolve()
data = json.loads(allowlist.read_text())
allowed = {pathlib.Path(item).resolve() for item in data.get("executables", []) if isinstance(item, str)}
if exe not in allowed:
    print(f"Refusing unlisted executable: {exe}", file=sys.stderr)
    print("Add its absolute /games/... path to /config/allowlist.json first.", file=sys.stderr)
    raise SystemExit(4)
PY

mkdir -p "$WINEPREFIX"
Xvfb "$DISPLAY" -screen 0 1280x720x24 -ac +extension GLX +render -noreset >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!
fluxbox >/tmp/fluxbox.log 2>&1 &
FLUXBOX_PID=$!
x11vnc -display "$DISPLAY" -forever -shared -rfbport 5900 -nopw -localhost >/tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!
websockify --web=/usr/share/novnc/ 6080 localhost:5900 >/tmp/novnc.log 2>&1 &
NOVNC_PID=$!

cleanup() {
  kill "$NOVNC_PID" "$X11VNC_PID" "$FLUXBOX_PID" "$XVFB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

sleep 2
echo "Native game viewer ready at http://127.0.0.1:6080/vnc.html?autoconnect=1&resize=remote"
echo "Launching allowlisted executable: $resolved_game"
wine "$resolved_game"
