from flask import redirect, session, render_template, request, Blueprint, Markup
import json
import markdown2
from server.functions.problem import get_all_problem_with_status, get_problem_data, update_problem
from server.functions.file_read import get_code, get_iodata, get_problem_body
from server.functions.user import is_admin
from server.functions.submission import save_submission
from server import base_url, config_file

route_problem = Blueprint(__name__, "problem")

# 問題追加ページ(管理者のみ)
@route_problem.route(base_url + "/add_problem", methods=["GET", "POST"])
def add_problem_route():
    # 管理者かどうか確認
    if not is_admin(session["user_id"]):
        return redirect(base_url)

    add_failed = None

    # 問題追加
    if request.method == "POST":
        problem_name = request.form["problem_name"]
        scoring = int(request.form["scoring"])
        open_date = request.form["open_date"]
        open_time = request.form["open_time"]
        problem_body = request.form["problem_body"]
        io_data = request.form["io_data"]

        add_failed = add_problem(problem_name, scoring, open_date, open_time, problem_body, io_data)

    return render_template("add_problem.html",
                           session=session["user_id"],
                           add_failed=add_failed)


# 問題編集ページ(管理者のみ)
@route_problem.route(base_url + "/edit_problem/<path:problem_id>", methods=["GET", "POST"])
def edit_problem_route(problem_id):
    # 管理者かどうか確認
    if not is_admin(session["user_id"]):
        return redirect(base_url)

    update_failed = None

    # 問題更新(POSTのとき)
    if request.method == "POST":
        problem_name = request.form["problem_name"]
        scoring = int(request.form["scoring"])
        open_date = request.form["open_date"]
        open_time = request.form["open_time"]
        problem_body = request.form["problem_body"]
        io_data = request.form["io_data"]

        update_failed = update_problem(problem_id, problem_name, scoring, open_date,
                                       open_time, problem_body, io_data)

    # 必要な情報を読み込む
    problem_data = get_problem_data(problem_id)
    iodata = json.loads(get_iodata(problem_id, config_file["system"]["password"]))
    iodata_format = json.dumps(iodata, indent=4)
    problem_body = get_problem_body(problem_id)

    return render_template("edit_problem.html",
                           session=session["user_id"],
                           problem=problem_data,
                           problem_iodata=iodata_format,
                           problem_body=problem_body,
                           update_failed=update_failed)


# 問題一覧表示ページ
@route_problem.route(base_url + "/problem_list")
def problem_list_view():
    now_page = request.args.get("page", 1, type=int)

    return render_template("problem_list.html",
                            session=session["user_id"],
                            now_page=now_page,
                            problem_list=get_all_problem_with_status(session["user_id"]))


# 問題情報表示ページ
@route_problem.route(base_url + "/problem/<path:problem_id>", methods=["GET", "POST"])
def problem_view(problem_id):
    # コード提出(POST)
    if request.method == "POST":
        save_submission(session["user_id"], problem_id,
                        request.form["submission_lang"],
                        request.form["submission_code"])

        return redirect(base_url + "/submission_list/all")

    # 問題ページ描画
    problem_body = markdown2.markdown(get_problem_body(problem_id), extras=['fenced-code-blocks'])
    if problem_body is None:
        return abort(404)

    return render_template("problem.html",
                            session=session["user_id"],
                            problem_body=Markup(problem_body))


