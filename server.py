#!/usr/bin/env python3
"""Small dependency-free server for the Codespace FNF web-build launcher."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import re

ROOT = Path(__file__).resolve().parent
MODS = ROOT / "mods"
PORT = int(os.environ.get("PORT", "8080"))


def safe_slug(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/api/mods":
            mods = []
            if MODS.exists():
                for folder in sorted(MODS.iterdir(), key=lambda p: p.name.lower()):
                    if folder.is_dir() and safe_slug(folder.name) and (folder / "index.html").is_file():
                        mods.append({"slug": folder.name, "name": folder.name.replace("-", " ").replace("_", " ").title()})
            body = json.dumps(mods).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    MODS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"FNF Codespace Player listening on http://0.0.0.0:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
