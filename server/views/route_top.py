from flask import render_template, request, session, redirect, Blueprint
from server import no_login_ok_url
from server import base_url


route_top = Blueprint(__name__, "top")

# リクエストが飛んできたらまずここに来る
@route_top.before_request
def before_request():
    if "user_id" not in session.keys():
       session["user_id"] = None

    # ログインが必要なURLかどうか判定
    enough_login = True
    for url in no_login_ok_url:
        if url in request.url:
            enough_login = False

    if enough_login and session["user_id"] is None:
        return redirect(base_url + "/login")

# トップページ
@route_top.route(base_url + "/")
def index():
    return render_template("index.html",
                           session=session["user_id"])


