# Your authorized ROMs

Place only ROMs you own or are authorized to use in a system subfolder. This repository intentionally contains no commercial ROMs or BIOS files.

Examples:

```text
roms/nes/my-game.nes
roms/snes/my-game.sfc
roms/genesis/my-game.md
roms/gb/my-game.gb
roms/gba/my-game.gba
roms/psp/my-game.iso
```

PSP images may use `.iso` or `.cso`. Keep them local; ROM files are ignored by Git and are not included in the public repository.

## Build an offline catalog

From the repository root, catalog only files already in your local `roms/` directory:

```bash
python3 tools/catalog_local_roms.py
```

This writes `roms_catalog.json` with each local file's title, platform, filename, relative path, byte size, and SHA-256 checksum. It does not contact ROM sites, fetch download endpoints, or download game files.
