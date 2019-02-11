from flask import request, redirect, render_template, session, Blueprint
from server.functions.user import get_user_data, update_user_data, change_password, is_admin
from server import base_url


route_user = Blueprint(__name__, "user")

# ユーザ設定ページ
@route_user.route(base_url + "/user_page", methods=["POST", "GET"])
def user_page():
    if session["user_id"] is None:
        return redirect(base_url)

    update_succeeded = None

    # データ更新(POST)
    if request.method == "POST":
        user_name = request.form["name"]
        open_code = int(request.form["open_code"])
        update_succeeded = update_user_data(session["user_id"], user_name, open_code)

    # 設定ページに必要な情報取得
    user_info = get_user_data(session["user_id"])
    if user_info is None:
        return redirect(base_url)

    return render_template("user_page.html",
                           user=user_info,
                           update_succeeded=update_succeeded,
                           session=session["user_id"])


# パスワード変更ページ
@route_user.route(base_url + "/change_password", methods=["POST", "GET"])
def change_password_route():
    if session["user_id"] is None:
        return redirect(base_url)

    change_succeeded = None

    # パスワード更新
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        new_password_conf = request.form["new_password_conf"]
        change_succeeded = change_password(session["user_id"],
                                           old_password,
                                           new_password,
                                           new_password_conf)

    return render_template("change_password.html",
                           session=session["user_id"],
                           change_succeeded=change_succeeded)


