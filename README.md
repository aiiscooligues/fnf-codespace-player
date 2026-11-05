# FNF Codespace Player

Play legally obtained **browser/web builds** of Friday Night Funkin' mods inside a GitHub Codespace. The project provides a small local launcher, forwards one HTTP port, and keeps each mod isolated in its own folder.

> This repository does not include Friday Night Funkin' or any third-party mod files. Only add files you have permission to use. Native Windows/Linux executables are not browser-compatible; use a mod's HTML5/WebGL export or another web build.

## Quick start in GitHub Codespaces

1. Create a Codespace from this repository.
2. Add one extracted web build under `mods/<mod-name>/`.
3. Make sure that folder contains the build's entry file, usually `index.html`.
4. Run:

   ```bash
   ./start.sh
   ```

5. Open port **8080** in the Ports panel. The launcher will list every folder in `mods/` that contains an `index.html`.
6. Pick a mod and click **Play**.

If the Codespace does not automatically forward port 8080, add it manually in the Ports panel and set its visibility to the level you want. Do not make a port public unless you understand that anyone with the URL may be able to access the running game.

## Adding a mod

```text
mods/
└── my-mod/
    ├── index.html
    ├── assets/
    ├── game.js
    └── ...
```

Preserve the web build's relative folder structure. Do not place an archive in `mods/`; extract it first. The launcher loads the build at `/mods/my-mod/index.html` so relative JavaScript, audio, images, and data files continue to work.

The included `mods/README.md` explains the expected layout.

## Automatic downloads

The optional installer in `tools/install_mods.py` downloads only the URLs you explicitly put in a manifest. It accepts HTTPS ZIP archives, checks an optional SHA-256 checksum, rejects path-traversal entries, requires an `index.html`, and refuses to overwrite an existing mod unless `--force` is supplied.

Copy the example and replace it with release URLs from sources you trust and are allowed to use:

```bash
cp mods/manifest.example.json mods/manifest.json
python3 tools/install_mods.py --manifest mods/manifest.json --dry-run
python3 tools/install_mods.py --manifest mods/manifest.json
```

Use direct release-asset URLs rather than scraping mod pages. Keep `mods/manifest.json` private or add it to `.gitignore` if it contains download links you do not want to publish. The script intentionally does not guess what “popular” means, scrape websites, bypass access controls, or download native desktop builds.

## Local use

Requires Python 3. Run:

```bash
./start.sh
```

Then open <http://localhost:8080>.

You can also choose a different port:

```bash
PORT=3000 ./start.sh
```

## What this supports

- HTML5, WebGL, or similar browser exports of FNF mods
- Multiple mods in one Codespace
- Relative assets, audio, JavaScript, and data files
- A forwarded Codespaces port with no Node.js dependency

## What this does not support

- Native `.exe`, `.app`, or Linux binary mods
- Mods that require a desktop engine or native filesystem access
- Circumventing DRM, paid access, or distribution restrictions

## Native Windows builds

An optional Wine/noVNC runner is included under `native-runner/`. It runs one explicitly allowlisted `.exe` inside an isolated container and exposes its virtual desktop on port `6080`. Read [`native-runner/README.md`](native-runner/README.md) before using it; keep that port private because it provides interactive control of the running game.

## License

The launcher code in this repository is released under the MIT License. Mod files remain under their respective authors' licenses; check each mod's terms before uploading or sharing them.
