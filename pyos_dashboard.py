#!/usr/bin/env python3
# Simple dashboard using Python standard library (no Flask)

import http.server
import socketserver
import socket
import threading
import subprocess
import urllib.parse
import html
import sys

PORT = 5000

APPS = {
    "notepad": "apps/notepad.py",
    "calculator": "apps/calculator.py",
    "filemanager": "apps/filemanager.py",
    "terminal": "apps/terminal.py",
}

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>PyOS Dashboard (no-framework)</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #121212; color: #eee; }}
    #main {{ width: 720px; margin: 30px auto; }}
    input[type=text] {{ width: 70%; padding: 10px; font-size: 16px; }}
    button {{ padding: 10px 14px; font-size: 16px; }}
    .msg {{ margin-top: 16px; padding: 10px; background: #222; border-radius: 6px; }}
    a {{ color: #7fc7ff; }}
  </style>
</head>
<body>
  <div id="main">
    <h1>PyOS Dashboard (no-framework)</h1>
    <form method="POST" action="/">
      <input name="cmd" autofocus placeholder="Type command: notepad, calculator, filemanager, terminal" />
      <button type="submit">Run</button>
    </form>
    {resp_block}
    <hr/>
    <div><strong>Available apps:</strong></div>
    <ul>
      {apps_list}
    </ul>
    <div style="font-size:12px;color:#aaa;margin-top:10px;">
      Note: In Codespaces you may need to forward the app ports to open them in the browser.
    </div>
  </div>
</body>
</html>
"""

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def launch_app(app_name):
    script = APPS.get(app_name)
    if not script:
        return None, "Unknown app"
    port = find_free_port()
    # Start as a new process; it will bind to the given port
    try:
        subprocess.Popen([sys.executable, script, str(port)])
        return port, None
    except Exception as e:
        return None, str(e)

class Handler(http.server.BaseHTTPRequestHandler):
    def _render(self, resp_block=""):
        apps_list = "\n".join(f"<li><b>{html.escape(k)}</b></li>" for k in APPS.keys())
        body = HTML_TEMPLATE.format(resp_block=resp_block, apps_list=apps_list)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        self._render()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = urllib.parse.parse_qs(body)
        cmd = data.get("cmd", [""])[0].strip()
        resp_block = ""
        if cmd:
            if cmd in APPS:
                port, err = launch_app(cmd)
                if port:
                    link = f"http://localhost:{port}/"
                    resp_block = f'<div class="msg">Launched <b>{html.escape(cmd)}</b> on <a href="{link}" target="_blank">{html.escape(link)}</a></div>'
                else:
                    resp_block = f'<div class="msg">Failed to launch <b>{html.escape(cmd)}</b>: {html.escape(err or "unknown")}</div>'
            else:
                resp_block = f'<div class="msg">Unknown command: <b>{html.escape(cmd)}</b></div>'
        else:
            resp_block = '<div class="msg">No command provided.</div>'
        self._render(resp_block=resp_block)

if __name__ == "__main__":
    with socketserver.ThreadingTCPServer(("", PORT), Handler) as httpd:
        print(f"Dashboard running at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down dashboard")
            httpd.server_close()
