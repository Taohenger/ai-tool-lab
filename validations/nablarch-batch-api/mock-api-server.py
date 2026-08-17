#!/usr/bin/env python3
"""Nablarch batch から呼び出されるモック API サーバ。

GET /hello        -> {"message":"hello from mock api","server":"mock","time":<ts>}
GET /healthz      -> {"status":"ok"}
POST /echo        -> エコーバック: 受け取った body を {"echo":<body>} で返す

起動: python3 mock-api-server.py [port]
既定ポート: 18090
"""
import json
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    server_version = "nablarch-mock-api/1.0"

    def _send(self, code: int, body: dict):
        payload = (json.dumps(body, ensure_ascii=False) + "\n").encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        now = datetime.now(timezone.utc).isoformat()
        if self.path in ("/", "/hello"):
            self._send(200, {"message": "hello from mock api",
                             "server": "mock",
                             "time": now,
                             "path": self.path})
        elif self.path == "/healthz":
            self._send(200, {"status": "ok", "time": now})
        else:
            self._send(404, {"status": "not found", "path": self.path})

    def do_POST(self):
        now = datetime.now(timezone.utc).isoformat()
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length).decode("utf-8", errors="replace") if length else ""
        if self.path == "/echo":
            self._send(200, {"echo": body, "received_at": now,
                             "content_type": self.headers.get("Content-Type", "")})
        else:
            self._send(404, {"status": "not found", "path": self.path})

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[mock-api] {self.address_string()} - {fmt % args}\n")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18090
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[mock-api] listening on http://127.0.0.1:{port}", file=sys.stderr, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == "__main__":
    main()
