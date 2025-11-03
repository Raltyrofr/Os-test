from flask import Flask, render_template_string, request, redirect, url_for
import subprocess
import threading
import socket

app = Flask(__name__)

# Apps and their startup commands
APPS = {
    "notepad": "apps/notepad.py",
    "calculator": "apps/calculator.py",
    "filemanager": "apps/filemanager.py",
    "terminal": "apps/terminal.py",
}

# Dynamic port assignment for new apps
def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def launch_app(app_name):
    if app_name in APPS:
        port = find_free_port()
        # Start the app in a new process/thread on an available port
        # Pass port as env variable or command line argument
        def run_app():
            subprocess.Popen(["python", APPS[app_name], str(port)])
        threading.Thread(target=run_app).start()
        return port
    return None

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PyOS Dashboard</title>
    <style>
        body { font-family: Arial; background: #222; color: #eee; }
        #main { width: 500px; margin: auto; }
        input { width: 80%; padding: 10px; font-size: 18px; }
        .cmd { padding: 5px; margin: 5px 0; background: #333;}
        a { color: #7fc7ff; }
    </style>
</head>
<body>
    <div id="main">
        <h2>PyOS Dashboard</h2>
        <form method="POST">
            <input autofocus name="cmd" placeholder="Type command (notepad, calculator, filemanager, terminal)" />
            <button type="submit">Run</button>
        </form>
        {% if resp %}
        <div class="cmd">
            {{ resp | safe }}
        </div>
        {% endif %}
        <hr>
        <b>Available Apps:</b>
        <ul>
        {% for k in apps %}
        <li><b>{{k}}</b></li>
        {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    resp = ""
    if request.method == "POST":
        cmd = request.form.get("cmd").strip()
        if cmd in APPS:
            port = launch_app(cmd)
            if port:
                resp = f"Launching <b>{cmd}</b> on <a href='http://localhost:{port}' target='_blank'>port {port}</a>"
            else:
                resp = f"Failed to launch app."
        else:
            resp = "Unknown command/app."
    return render_template_string(TEMPLATE, resp=resp, apps=APPS.keys())

if __name__ == "__main__":
    app.run(port=5000, debug=True)
