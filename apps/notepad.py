#!/usr/bin/env python3
# Simple notepad app using http.server (no external libs)

import sys
import http.server
import socketserver
import urllib.parse
import html

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6001

saved_text = ""

HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Notepad</title>
<style>body{{background:#222;color:#eee;font-family:Arial}}textarea{{width:95%;height:60vh;font-size:16px}}</style>
</head>
<body>
<h2>Notepad</h2>
<form method="POST" action="/">
<textarea name="text">{text}</textarea><br/>
<input type="submit" value="Save" />
</form>
<div style="margin-top:10px;color:lightgreen">{msg}</div>
</body></html>
"""

class NotepadHandler(http.server.BaseHTTPRequestHandler):
    def _respond(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_GET(self):
        global saved_text
        body = HTML.format(text=html.escape(saved_text), msg="")
        self._respond(body)

    def do_POST(self):
        global saved_text
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(data)
        saved_text = parsed.get("text", [""])[0]
        body = HTML.format(text=html.escape(saved_text), msg="Saved!")
        self._respond(body)

if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("", PORT), NotepadHandler) as httpd:
        print(f"Notepad running at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
