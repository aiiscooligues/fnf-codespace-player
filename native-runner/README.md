# Native FNF runner (Wine + noVNC)

This optional service runs a **specific, allowlisted Windows executable** inside Wine and exposes its virtual desktop through noVNC on port `6080`. It is separate from the browser web-build launcher on port `8080`.

This is intended for legally obtained native builds. Do not use it to bypass DRM or access controls. Keep port 6080 private; a public VNC viewer can control the running game.

## Setup

From the repository root:

```bash
mkdir -p native-runner/games native-runner/config
cp native-runner/allowlist.example.json native-runner/config/allowlist.json
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
