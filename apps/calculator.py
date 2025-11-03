#!/usr/bin/env python3
# Calculator: binds to 0.0.0.0
import sys
import http.server
import socketserver
import urllib.parse
import html
import ast
import operator as op

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6002

ALLOWED_OPERATORS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg, ast.UAdd: op.pos,
    ast.FloorDiv: op.floordiv
}

def safe_eval(expr):
    def _eval(node):
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            oper = ALLOWED_OPERATORS.get(type(node.op))
            if oper is None:
                raise ValueError("Unsupported operator")
            return oper(left, right)
        if isinstance(node, ast.UnaryOp):
            oper = ALLOWED_OPERATORS.get(type(node.op))
            if oper is None:
                raise ValueError("Unsupported unary operator")
            return oper(_eval(node.operand))
        raise ValueError("Unsupported expression")
    parsed = ast.parse(expr, mode='eval')
    return _eval(parsed.body)

HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Calculator</title>
<style>body{{background:#1b1b1b;color:#eee;font-family:Arial}}input[type=text]{{width:300px;padding:8px;font-size:16px}}</style>
</head>
<body>
<h2>Calculator</h2>
<form method="POST" action="/">
<input name="expr" value="{expr}" placeholder="Enter expression, e.g. 2+2*3" />
<input type="submit" value="=" />
</form>
<div style="margin-top:10px;color:#9f9">{res}</div>
</body></html>
"""

class CalcHandler(http.server.BaseHTTPRequestHandler):
    def _respond(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def do_GET(self):
        self._respond(HTML.format(expr="", res=""))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(length).decode("utf-8")
        parsed = urllib.parse.parse_qs(data)
        expr = parsed.get("expr", [""])[0]
        res = ""
        if expr.strip():
            try:
                val = safe_eval(expr)
                res = str(val)
            except Exception as e:
                res = "Error: " + str(e)
        self._respond(HTML.format(expr=html.escape(expr), res=html.escape(res)))

if __name__ == "__main__":
    print(f"Calculator running on 0.0.0.0:{PORT}")
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), CalcHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
