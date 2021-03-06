from flask import request, redirect, render_template, session, Blueprint
from server.functions.user import get_user_data, update_user_data, change_password, is_admin
from server.functions.rate import get_user_rate_data, get_user_rate_trans_data
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
    rate_trans_info = get_user_rate_trans_data(session["user_id"])
    user_rate_data = get_user_rate_data(session["user_id"])
    user_info = get_user_data(session["user_id"])
    if user_info is None:
        return redirect(base_url)

    return render_template("user_page.html",
                           user=user_info,
                           rate_labels=["YEC No.1", "YEC No.2", "YEC No.3", "YEC No.4"],
                           update_succeeded=update_succeeded,
                           session=session["user_id"],
                           rate=user_rate_data,
                           rate_trans_info=rate_trans_info)


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
                                           new_password_conf,
                                           False)

    return render_template("change_password.html",
                           session=session["user_id"],
                           change_succeeded=change_succeeded)


# パスワードリセットページ
@route_user.route(base_url + "/reset_password", methods=["POST", "GET"])
def reset_password_route():
    if session["user_id"] is None:
        return redirect(base_url)

    change_succeeded = None

    # パスワード更新
    if request.method == "POST":
        user_id = request.form["user_id"]
        new_password = request.form["new_password"]
        new_password_conf = request.form["new_password_conf"]
        change_succeeded = change_password(user_id,
                                          "old_pass",
                                          new_password,
                                          new_password_conf,
                                          True)

    return render_template("reset_password.html",
                           session=session["user_id"],
                           change_succeeded=change_succeeded)
