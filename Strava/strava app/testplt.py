import base64
from io import BytesIO

from flask import Flask, redirect, url_for
from matplotlib.figure import Figure

app = Flask(__name__)

@app.route("/admin")
def admin():
	return redirect(url_for("home"))

@app.route("/")
def hello():
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"





"""
To run the application, use the flask command or python -m flask. You need to tell the Flask where your application is with the --app option.
In below example, hello is hello.py (dont enter extension) and you need to run from directory where file is located.

$ flask --app hello run
 * Serving Flask app 'hello'
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 """