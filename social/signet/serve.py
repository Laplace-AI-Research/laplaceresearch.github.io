"""Local render server for the Signet brand plates (development only; never deployed).

    python3 social/signet/serve.py [port]

Serves the site root, and accepts POST /save?path=<relative path> from render.html to write a rendered PNG/SVG.
Writes are limited to social/signet/out/ and assets/signet/.
"""
import http.server
import pathlib
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
ALLOWED = [ROOT / "social/signet/out", ROOT / "assets/signet"]


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        rel = q.get("path", [""])[0]
        dest = (ROOT / rel).resolve()
        if not rel or not any(str(dest).startswith(str(a)) for a in ALLOWED):
            self.send_response(403); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.rfile.read(n))
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        print("saved", dest.relative_to(ROOT), flush=True)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
