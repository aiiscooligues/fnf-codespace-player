# Requested mod sources

The Codespace launcher can only run a mod that has an HTML5/WebGL-style web build with an `index.html`. Do not place `.exe`, `.app`, or native Linux builds in `mods/`.

## Indie Cross

- Browser-playable page: <https://botstudio.itch.io/indiecross>
- The page identifies itself as **FNF Indie Cross Test** and says it can be played on the web.
- This is a test build, not necessarily the full official Indie Cross release. The original project page is linked from the page: <https://gamejolt.com/games/indiecross/643540>
- The downloadable files shown on the page are desktop ZIPs, so they are not suitable for this Codespace unless the author provides an authorized web ZIP.

## Mario's Madness

- Project page: <https://gamejolt.com/games/mariosmadness/693301>
- The page provides desktop downloads and mirrors for V2. It does not provide an HTML5/WebGL ZIP, so those files cannot be launched by this browser-only player.

## Falter Alters

- GameBanana listing: <https://gamebanana.com/mods/462702>
- The listing is for a chart/remix update and does not provide a verified browser build. It should not be added to the web-mod installer unless its author publishes an authorized HTML5/WebGL build.

## Adding an authorized web build

When an author provides a direct web ZIP, add it to `manifest.json`:

```json
[
  {
    "name": "indie-cross-web",
    "url": "https://trusted-author.example/indie-cross-web.zip",
    "sha256": "optional-64-character-sha256-checksum"
  }
]
```

Then run:

```bash
python3 tools/install_mods.py --manifest mods/manifest.json
```
