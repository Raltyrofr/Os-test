import sys, os
from flask import Flask, render_template_string, request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6003

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>File Manager</title></head>
<body style="background:#333;color:#edf;">
<h2>PyOS File Manager</h2>
<form method="POST">
Browse: <input name="path" value="{{path}}" style="width:350px;" />
<input type="submit" value="Go" />
</form>
<ul>
{% for f in files %}
<li>{{f}}</li>
{% endfor %}
</ul>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def fm():
    path = "."
    if request.method == "POST":
        path = request.form.get("path", ".")
    try:
        files = os.listdir(path)
    except Exception as e:
        files = [str(e)]
    return render_template_string(HTML, files=files, path=path)

if __name__ == "__main__":
    app.run(port=PORT, debug=False)
