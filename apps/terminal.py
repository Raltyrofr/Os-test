#!/usr/bin/env python3
# Terminal: binds to 0.0.0.0 (WARNING: executes commands)
import sys
import http.server
import socketserver
import urllib.parse
import subprocess
import html

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6004

HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Terminal</title>
<style>body{{background:#0d0d0d;color:#dcdcdc;font-family:monospace}}input[type=text]{{width:70%;padding:8px}}</style>
</head>
<body>
<h2>Terminal</h2>
<form method="POST" action="/">
<input name="cmd" autofocus placeholder="Enter shell command, e.g. ls -la" value="{cmd}" />
<input type="submit" value="Run" />
</form>
<pre style="background:#111;color:#bfbfbf;padding:10px;border-radius:4px">{out}</pre>
</body></html>
"""

class TermHandler(http.server.BaseHTTPRequestHandler):
    def _respond(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_GET(self):
        self._respond(HTML.format(cmd="", out=""))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(data)
        cmd = parsed.get("cmd", [""])[0]
        out = ""
        if cmd.strip():
            try:
                out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10).decode("utf-8", errors="replace")
            except subprocess.CalledProcessError as e:
                out = e.output.decode("utf-8", errors="replace")
            except Exception as e:
                out = str(e)
        self._respond(HTML.format(cmd=html.escape(cmd), out=html.escape(out)))

if __name__ == "__main__":
    print(f"Terminal running on 0.0.0.0:{PORT}")
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), TermHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
