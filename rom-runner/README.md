# Legal ROM runner (RetroArch + noVNC)

This optional service plays ROM files that you own or are authorized to use. It does not connect to ROM sites, download copyrighted games, bypass protections, or include BIOS files. ROMs are mounted read-only and the viewer is bound to localhost by default.

## Supported cores

| System | Core value | Typical extensions |
| --- | --- | --- |
| NES | `nestopia` | `.nes`, `.fds` |
| SNES | `snes9x` | `.sfc`, `.smc` |
| Genesis / Mega Drive | `genesis_plus_gx` | `.md`, `.gen`, `.bin` |
| Game Boy / Color | `gambatte` | `.gb`, `.gbc` |
| Game Boy Advance | `mgba` | `.gba` |
| PSP | `ppsspp` | `.iso`, `.cso` |

Additional systems require adding a compatible RetroArch core and, for some systems, a BIOS file that you legally obtained. “Any ROM” is not guaranteed because ROM formats and emulator requirements differ.

## Setup

From the repository root, put your own ROM in the matching folder:

```text
roms/
├── nes/my-game.nes
├── snes/my-game.sfc
├── genesis/my-game.md
├── gb/my-game.gb
└── gba/my-game.gba
```

Build and start the runner. Examples:

```bash
cd rom-runner
ROM_PATH=/roms/nes/my-game.nes CORE=nestopia docker compose up --build
```

```bash
cd rom-runner
ROM_PATH=/roms/gba/my-game.gba CORE=mgba docker compose up --build
```

For PSP:

```bash
cd rom-runner
ROM_PATH=/roms/psp/my-game.iso CORE=ppsspp docker compose up --build
```

Put PSP images under `roms/psp/`. The runner includes the PPSSPP libretro core; PSP performance depends heavily on the Codespace CPU, and some games may be too demanding for a software-rendered virtual display.

The PSP launch defaults are tuned for speed: JIT CPU core, fast memory, 1x native resolution, OpenGL, and adaptive frameskip. Override them for a specific game:

```bash
cd rom-runner
PPSSPP_INTERNAL_RESOLUTION=960x544 \
PPSSPP_AUTO_FRAMESKIP=disabled \
PPSSPP_FRAMESKIP=0 \
ROM_PATH=/roms/psp/my-game.iso CORE=ppsspp docker compose up --build
```

For the best baseline, start with the defaults. If the game is slow, keep `480x272`, leave adaptive frameskip enabled, and avoid texture upscaling. If it is stable and you want sharper output, try `960x544`. The biggest improvement comes from choosing a Codespace with more CPU; Xvfb/noVNC is software-rendered and does not provide GPU acceleration.

Forward port **6090** in Codespaces and open:

```text
/vnc.html?autoconnect=1&resize=remote
```

Stop with `Ctrl-C` or `docker compose down`. Keep port 6090 private because the noVNC session provides interactive keyboard control.
