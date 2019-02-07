from flask import render_template, request, session, redirect, Blueprint
from server.functions.contest import get_3type_divided_contest, get_contest_problems, get_contest_data, get_ranking_data, add_contest
from server.functions.user import is_admin
from server.functions.problem import get_all_problem
from server import base_url

route_contest = Blueprint(__name__, "contest")

# コンテスト追加ページ(管理者のみ)
@route_contest.route(base_url + "/add_contest", methods=["GET", "POST"])
def add_contest_route():
    # 管理者かどうか確認
    if not is_admin(session["user_id"]):
        return redirect(base_url)

    add_failed = None

    # 問題追加
    if request.method == "POST":
        contest_name = request.form["contest_name"]
        start_date = request.form["start_date"]
        start_time = request.form["start_time"]
        end_date = request.form["end_date"]
        end_time = request.form["end_time"]
        problems = request.form.getlist("problems")

        add_failed = add_contest(contest_name, start_date+" "+start_time, end_date+" "+end_time, problems)

    return render_template("add_contest.html",
                           session=session["user_id"],
                           add_failed=add_failed,
                           problems=get_all_problem(session["user_id"], False))


# コンテスト一覧表示ページ
@route_contest.route(base_url + "/contest_list")
def contest_list_view():
    now_page = request.args.get("page", 1, type=int)
    past_contest, now_contest, future_contest = get_3type_divided_contest()

    return render_template("contest_list.html",
                            session=session["user_id"],
                            past_contest=past_contest,
                            now_contest=now_contest,
                            now_page=now_page,
                            future_contest=future_contest)


# コンテスト情報表示ページ
@route_contest.route(base_url + "/contest/<path:contest_id>")
def contest_view(contest_id):
    ranking_data, submission_data = get_ranking_data(contest_id)

    return render_template("contest.html",
                           session=session["user_id"],
                           contest_data=get_contest_data(contest_id),
                           ranking_list=ranking_data,
                           submission_data=submission_data,
                           problem_list=get_contest_problems(contest_id, session["user_id"]))


