from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from login_process import register, login
from problem import get_all_problem
from contest import get_3type_divided_contest

# Flask
app = Flask(__name__)
app.config.from_pyfile("config.cfg")
bootstrap = Bootstrap(app)

# Other
base_url = "/yuge_micom_ojs"

#Routes
@app.before_request
def before_request():
    if "user_id" not in session.keys():
        session["user_id"] = None


@app.route(base_url + "/")
def index():
    return render_template("index.html",
                           session=session["user_id"])


@app.route(base_url + "/register", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("register.html",
                               session=session["user_id"])

    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    password = request.form["password"]
    password_conf = request.form["password_conf"]

    # ユーザ登録
    if register(user_id, user_name, password, password_conf):
        session["user_id"] = user_id
        return redirect("/yuge_micom_ojs")
    else:
        return render_template("register.html",
                               inp_failed="Failed",
                               session=session["user_id"])


@app.route(base_url + "/login", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login.html",
                               session=session["user_id"])

    user_id = request.form["user_id"]
    password = request.form["password"]

    # 認証
    if login(user_id, password):
        session["user_id"] = user_id
        return redirect(base_url)
    else:
        return render_template("login.html",
                               login_failed="Failed",
                               session=session["user_id"])


@app.route(base_url + "/logout")
def logout_user():
    session["user_id"] = None
    return redirect(base_url)


@app.route(base_url + "/contest/")
def contest_view():
    past_contest, now_contest, future_contest = get_3type_divided_contest()

    return render_template("contest_list.html",
                           session=session["user_id"],
                           past_contest=past_contest,
                           now_contest=now_contest,
                           future_contest=future_contest)


@app.route(base_url + "/problem/")
def problem_view():
    return render_template("problem_list.html",
                           session=session["user_id"],
                           problem_list=get_all_problem())

if __name__ == '__main__':
    app.run(port=11000)
