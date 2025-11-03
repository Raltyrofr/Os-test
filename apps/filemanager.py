#!/usr/bin/env python3
# Simple file manager using the standard library

import sys
import http.server
import socketserver
import urllib.parse
import os
import html

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6003

HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>File Manager</title>
<style>body{{background:#161616;color:#eee;font-family:Arial}}input[type=text]{{width:60%;padding:8px}}</style>
</head>
<body>
<h2>File Manager</h2>
<form method="POST" action="/">
Path: <input name="path" value="{path}" />
<input type="submit" value="Go" />
</form>
<div style="margin-top:12px;">
<ul>
{items}
</ul>
</div>
</body></html>
"""

class FMHandler(http.server.BaseHTTPRequestHandler):
    def _respond(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_GET(self):
        self._respond(HTML.format(path=".", items=""))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(data)
        path = parsed.get("path", ["."])[0] or "."
        items_html = ""
        try:
            entries = os.listdir(path)
            entries.sort()
            for e in entries:
                full = os.path.join(path, e)
                if os.path.isdir(full):
                    items_html += f'<li>[DIR] {html.escape(e)}</li>'
                else:
                    items_html += f'<li>{html.escape(e)} ({os.path.getsize(full)} bytes)</li>'
        except Exception as exc:
            items_html = f"<li>Error: {html.escape(str(exc))}</li>"
        self._respond(HTML.format(path=html.escape(path), items=items_html))

if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("", PORT), FMHandler) as httpd:
        print(f"File Manager running at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
