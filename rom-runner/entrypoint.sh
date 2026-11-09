#!/usr/bin/env bash
set -Eeuo pipefail

: "${DISPLAY:=:99}"
: "${ROM_PATH:=}"
: "${CORE:=}"

if [[ -z "$ROM_PATH" || -z "$CORE" ]]; then
  echo "Set ROM_PATH and CORE. Example: ROM_PATH=/roms/nes/game.nes CORE=nestopia" >&2
  exit 2
fi

rom_root=$(realpath -e /roms)
rom=$(realpath -e -- "$ROM_PATH")
case "$rom" in
  "$rom_root"/*) ;;
  *) echo "Refusing ROM outside /roms: $ROM_PATH" >&2; exit 3 ;;
esac
[[ -f "$rom" ]] || { echo "ROM not found: $rom" >&2; exit 4; }

case "$CORE" in
  nestopia|snes9x|genesis_plus_gx|mgba|gambatte|ppsspp) ;;
  *) echo "Unsupported core: $CORE" >&2; exit 5 ;;
esac

core_path=$(find /usr/lib /usr/libexec -type f \( -name "${CORE}_libretro.so" -o -name "libretro-${CORE}.so" -o -name "${CORE}.so" \) -print -quit 2>/dev/null || true)
if [[ -z "$core_path" ]]; then
  echo "RetroArch core not found for: $CORE" >&2
  find /usr/lib -iname '*libretro*.so' -print 2>/dev/null | head -30 >&2
  exit 6
fi

Xvfb "$DISPLAY" -screen 0 1280x720x24 -ac +extension GLX +render -noreset >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!
fluxbox >/tmp/fluxbox.log 2>&1 &
FLUXBOX_PID=$!
x11vnc -display "$DISPLAY" -forever -shared -rfbport 5901 -nopw -localhost >/tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!
websockify --web=/usr/share/novnc/ 6090 localhost:5901 >/tmp/novnc.log 2>&1 &
NOVNC_PID=$!

cleanup() { kill "$NOVNC_PID" "$X11VNC_PID" "$FLUXBOX_PID" "$XVFB_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM

sleep 2
echo "ROM viewer ready at http://127.0.0.1:6090/vnc.html?autoconnect=1&resize=remote"
echo "Core: $CORE"
echo "ROM: $rom"
retroarch --config /dev/null --verbose --fullscreen --menu-unified-content yes -L "$core_path" "$rom"
