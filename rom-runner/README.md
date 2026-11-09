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

Forward port **6090** in Codespaces and open:

```text
/vnc.html?autoconnect=1&resize=remote
```

Stop with `Ctrl-C` or `docker compose down`. Keep port 6090 private because the noVNC session provides interactive keyboard control.
