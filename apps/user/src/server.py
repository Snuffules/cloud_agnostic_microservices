import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

SERVICE_NAME = os.getenv("SERVICE_NAME", "user")
PORT = int(os.getenv("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "service": SERVICE_NAME})
            return

        self._send_json(200, {"service": SERVICE_NAME, "message": "running"})


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"{SERVICE_NAME} listening on port {PORT}", flush=True)
    server.serve_forever()
