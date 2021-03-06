from flask import render_template, request, session, redirect, Blueprint
from server.functions.problem import get_all_problem_with_status
from server.functions.contest import get_all_contest
from server.functions.user import is_admin
from server import base_url, config_file

route_admin = Blueprint(__name__, "admin")

@route_admin.route(base_url + "/control_panel", methods=["GET"])
def control_panel_route():
    # 管理者かどうか判定
    if not is_admin(session["user_id"]):
        return redirect(base_url)

    # 必要な情報取得
    problem_list = get_all_problem_with_status(session["user_id"], False)
    contest_list = get_all_contest()

    return render_template("control_panel.html",
                           problem_list=problem_list,
                           contest_list=contest_list,
                           session=session["user_id"])

@route_admin.route(base_url + "/edit_config", methods=["GET", "POST"])
def edit_config_route():
    # 更新
    if request.method == "POST":
        # 入力受け取り
        config_file["docker"]["image_name"] = request.form["image_name"]
        config_file["user"]["register_rest"] = request.form["register_rest"]
        config_file["user"]["login_rest_users"] = request.form["login_rest_users"]

        # ファイル更新
        with open("config.ini", "w", encoding="utf-8") as f:
            config_file.write(f)
        config_file.read("config.ini")

        # リダイレクト
        redirect(base_url + "/edit_config")

    # 画面表示
    image_name = config_file["docker"]["image_name"]
    register_rest = config_file["user"].getboolean("register_rest")
    login_rest_users = config_file["user"]["login_rest_users"]

    return render_template("edit_config.html",
                           session=session["user_id"],
                           image_name=image_name,
                           login_rest_users=login_rest_users,
                           register_rest=register_rest)

