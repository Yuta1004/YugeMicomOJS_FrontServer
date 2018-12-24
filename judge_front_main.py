from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from login_process import register

# Flask
app = Flask(__name__)
bootstrap = Bootstrap(app)

# Other
base_url = "/yuge_micom_ojs"

#Routes
@app.route(base_url + "/")
def index():
    return render_template("index.html")


@app.route(base_url + "/register", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("register.html")

    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    password = request.form["password"]
    password_conf = request.form["password_conf"]

    if register(user_id, user_name, password, password_conf):
        return "Register Successful"
    else:
        return render_template("register.html", inp_failed="Failed")


@app.route(base_url + "/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    return "None"

if __name__ == '__main__':
    app.run(port=11000)
