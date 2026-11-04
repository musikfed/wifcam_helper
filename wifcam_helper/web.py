"""Loopback-only WifCam test dashboard (Python stdlib, no cookies, no credentials saved)."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import threading
from .bench import BenchError, conservative_preset, read_last, run_test, store

ROOT = Path(__file__).resolve().parents[1]
TOKEN = secrets.token_urlsafe(32)
TEST_LOCK = threading.Lock()
PORT = int(os.environ.get("WIFCAM_HELPER_PORT", "8765"))
if PORT < 1024 or PORT > 65535:
    raise ValueError("WIFCAM_HELPER_PORT must be 1024..65535")


class Handler(BaseHTTPRequestHandler):
    server_version = "WifCamHelper/0.1"
    def log_message(self, format, *args):
        # Never log URL or POST JSON: RTSP may include credentials.
        return

    def allowed(self) -> bool:
        host = self.headers.get("Host", "").lower()
        return host in (f"127.0.0.1:{PORT}", f"localhost:{PORT}", "127.0.0.1", "localhost")

    def send(self, data: bytes, *, mime: str = "application/json; charset=utf-8",
             code: int = 200, attachment: str = "") -> None:
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
        self.end_headers()
        self.wfile.write(data)

    def js(self, obj: object, code: int = 200, attachment: str = "") -> None:
        self.send((json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8"),
                  code=code, attachment=attachment)

    def do_GET(self) -> None:
        if not self.allowed():
            self.js({"error": "Unexpected Host header"}, 403)
            return
        if self.path == "/":
            html = (ROOT / "wifcam_helper/ui.html").read_text(encoding="utf-8")
            # Embed an ephemeral CSRF token only in this loopback-served page.
            html = html.replace("__CSRF_TOKEN__", TOKEN)
            self.send(html.encode("utf-8"), mime="text/html; charset=utf-8")
        elif self.path == "/api/i18n":
            loc = json.loads((ROOT / "locales/strings.json").read_text(encoding="utf-8"))
            self.js(loc)
        elif self.path == "/api/last":
            self.js(read_last() or {})
        elif self.path == "/api/preset":
            self.js(conservative_preset(), attachment="wifcam-approved-candidate.json")
        else:
            self.js({"error": "not found"}, 404)

    def do_POST(self) -> None:
        if not self.allowed() or self.path != "/api/run":
            self.js({"error": "not allowed"}, 403)
            return
        origin = self.headers.get("Origin", "")
        if origin and origin not in (f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"):
            self.js({"error": "Origin check failed"}, 403)
            return
        if self.headers.get("X-Lab-Token", "") != TOKEN:
            self.js({"error": "Session token required"}, 403)
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            self.js({"error": "JSON required"}, 415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 2 or length > 4096:
                raise ValueError("Invalid request length")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("Object required")
            keys = ("kind", "host", "user", "key", "url", "alt_url", "transport",
                    "mic_consent", "speaker_consent", "vision_consent", "model", "device",
                    "samples", "ollama_endpoint", "ollama_model", "question", "ollama_consent")
            if set(data) - set(keys):
                raise ValueError("Unsupported option")
            if not TEST_LOCK.acquire(blocking=False):
                self.js({"error": "A test is already running"}, 409)
                return
            try:
                result = run_test(
                    str(data.get("kind", "")), host=str(data.get("host", "")),
                    user=str(data.get("user", "root")), key=str(data.get("key", "")),
                    url=str(data.get("url", "")), alt_url=str(data.get("alt_url", "")), transport=str(data.get("transport", "tcp")),
                    mic_consent=data.get("mic_consent") is True,
                    speaker_consent=data.get("speaker_consent") is True,
                    vision_consent=data.get("vision_consent") is True,
                    model=str(data.get("model", "")), device=str(data.get("device", "cpu")),
                    samples=data.get("samples", 3),
                    ollama_endpoint=str(data.get("ollama_endpoint", "")),
                    ollama_model=str(data.get("ollama_model", "")),
                    question=str(data.get("question", "Что находится перед камерой?")),
                    ollama_consent=data.get("ollama_consent") is True,
                )
                doc = store(result)
            finally:
                TEST_LOCK.release()
            self.js(doc)
        except (BenchError, ValueError, TypeError, OSError, json.JSONDecodeError) as exc:
            # Helpers deliberately sanitize tool errors; no command stderr or credentials.
            self.js({"error": str(exc)}, 422)


def serve() -> None:
    print(f"WifCam Helper: http://127.0.0.1:{PORT} (loopback only; SSH tunnel for other computers)")
    with ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as server:
        server.serve_forever()
