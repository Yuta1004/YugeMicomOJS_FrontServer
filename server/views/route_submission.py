from flask import render_template, request, session, redirect, Blueprint
from server.functions.submission import get_submission_data, save_submission, get_data_for_submission_page
from server.functions.user import is_admin
from server.functions.judge import add_judge_job
from server import base_url

route_submission = Blueprint(__name__, "submission")

# 提出一覧表示ページ
@route_submission.route(base_url + "/submission_list/<path:user_id>")
def submission_list_view(user_id):
    now_page = request.args.get("page", 1, type=int)

    return render_template("submission_list.html",
                           session=session["user_id"],
                           now_page=now_page,
                           submission_data=get_submission_data(user_id, "all"))


# 提出情報表示ページ
@route_submission.route(base_url + "/submission/<path:submission_id>", methods=["GET", "POST"])
def submission_view(submission_id):
    # リジャッジ
    if "rejudge" in request.form.keys() and is_admin(session["user_id"]):
        add_judge_job(submission_id)
        return redirect(base_url + "/submission_list/all")

    # 提出詳細ページ描画に必要な情報を取得
    submission_data, code, open_code = get_data_for_submission_page(session["user_id"], submission_id)

    return render_template("submission.html",
                           session=session["user_id"],
                           submission_data=submission_data,
                           code=code,
                           open_code=open_code,
                           is_admin=is_admin(session["user_id"]))


