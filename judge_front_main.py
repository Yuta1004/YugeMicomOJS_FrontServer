from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

base_url = "/judge_system"

@app.route(base_url + "/")
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=11000)
