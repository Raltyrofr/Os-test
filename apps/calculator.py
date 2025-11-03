import sys
from flask import Flask, render_template_string, request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 6002

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Calculator</title></head>
<body style="background:#232c2e;color:#eee;">
<h2>PyOS Calculator</h2>
<form method="POST">
<input name="expr" placeholder="Enter expression" style="width:250px;font-size:22px;" value="{{expr or ''}}"/>
<input type="submit" value="=" />
</form>
{% if res is not none %}
<b>Result: </b> {{res}}
{% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calc():
    res, expr = None, ""
    if request.method == "POST":
        expr = request.form.get("expr", "")
        try:
            res = eval(expr)
        except:
            res = "Error"
    return render_template_string(HTML, res=res, expr=expr)

if __name__ == "__main__":
    app.run(port=PORT, debug=False)
