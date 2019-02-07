from flask import render_template, request, session, redirect, Blueprint
from server import no_login_ok_url
from server import base_url


route_top = Blueprint(__name__, "top")

# トップページ
@route_top.route(base_url + "/")
def index():
    return render_template("index.html",
                           session=session["user_id"])


