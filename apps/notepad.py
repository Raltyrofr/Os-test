import sys
from flask import Flask, render_template_string, request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6001

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Notepad</title></head>
<body style="background:#242424;color:#eee;">
<h2>PyOS Notepad</h2>
<form method="POST">
<textarea name="text" style="width:90%;height:400px;">{{txt}}</textarea><br>
<input type="submit" value="Save" />
</form>
{% if msg %}
<div style="color:lightgreen">{{msg}}</div>
{% endif %}
</body>
</html>
"""

saved_text = ""

@app.route("/", methods=["GET", "POST"])
def main():
    global saved_text
    msg = ''
    if request.method == "POST":
        saved_text = request.form.get("text", "")
        msg = "Saved!"
    return render_template_string(HTML, txt=saved_text, msg=msg)

if __name__ == "__main__":
    app.run(port=PORT, debug=False)
