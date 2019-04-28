from flask import render_template, request, session, redirect, Blueprint
from server.functions.login_process import register, login
from server import base_url, config_file

route_auth = Blueprint(__name__, "auth")

# ユーザ登録ページ
@route_auth.route(base_url + "/register", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("register.html",
                               register_rest=config_file["user"].getboolean("register_rest"),
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
                               register_rest=config_file["user"].getboolean("register_rest"),
                               session=session["user_id"])


# ログインページ
@route_auth.route(base_url + "/login", methods=["GET", "POST"])
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


# ログアウト(トップページにリダイレクト)
@route_auth.route(base_url + "/logout")
def logout_user():
    session["user_id"] = None
    return redirect(base_url)

