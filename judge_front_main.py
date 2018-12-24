from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

base_url = "/judge_system"

@app.route(base_url + "/")
def index():
    return render_template("index.html")


@app.route(base_url + "/register", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("register.html")

    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    password = request.form["password"]
    password_conf = request.form["password_conf"]

    return ""


if __name__ == '__main__':
    app.run(port=11000)
