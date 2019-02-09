from flask import render_template, request, session, redirect, Blueprint
from server.functions.problem import get_all_problem_with_status
from server.functions.contest import get_all_contest
from server.functions.user import is_admin
from server import base_url

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

