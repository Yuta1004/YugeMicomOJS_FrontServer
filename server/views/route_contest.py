from flask import render_template, request, session, redirect, Blueprint, Markup
from server.functions.contest import get_3type_divided_contest, get_contest_problems, get_contest_data, get_ranking_data
from server.functions.contest import add_contest, update_contest, get_hint_data, open_hint, get_contest_hint
from server.functions.user import is_admin
from server.functions.problem import get_all_problem_with_status
from server.functions.rate import update_contest_rate
from server.functions.file_read import get_contest_top
from server import base_url
import markdown2
from datetime import datetime
import json

route_contest = Blueprint(__name__, "contest")

# コンテスト追加ページ(管理者のみ)
@route_contest.route(base_url + "/add_contest", methods=["GET", "POST"])
def add_contest_route():
    # 管理者かどうか確認
    if not is_admin(session["user_id"]):
        return redirect(base_url)

    add_result = None

    # 問題追加
    if request.method == "POST":
        contest_name = request.form["contest_name"]
        contest_top = request.form["contest_top"]
        start_date = request.form["start_date"]
        start_time = request.form["start_time"]
        end_date = request.form["end_date"]
        end_time = request.form["end_time"]
        frozen_date = request.form["frozen_date"]
        frozen_time = request.form["frozen_time"]
        rate_limit = request.form["rate_limit"]
        problems = request.form.getlist("problems")
        hint_info = request.form["hint_info"]

        add_result = add_contest(contest_name, contest_top,
                                 start_date+" "+start_time, end_date+" "+end_time,
                                 frozen_date+" "+frozen_time,
                                 rate_limit, problems, hint_info)

    return render_template("add_contest.html",
                           session=session["user_id"],
                           add_result=add_result,
                           problems=get_all_problem_with_status(session["user_id"], False))


# コンテスト編集ページ(管理者のみ)
@route_contest.route(base_url + "/edit_contest/<path:contest_id>", methods=["GET", "POST"])
def edit_contest_route(contest_id):
    # 管理者かどうか確認
    if not is_admin(session["user_id"]):
        return redirect(base_url)

    update_result = None

    # 情報更新
    if request.method == "POST":
        contest_name = request.form["contest_name"]
        contest_top = request.form["contest_top"]
        start_date = request.form["start_date"]
        start_time = request.form["start_time"]
        end_date = request.form["end_date"]
        end_time = request.form["end_time"]
        frozen_date = request.form["frozen_date"]
        frozen_time = request.form["frozen_time"]
        rate_limit = request.form["rate_limit"]
        problems = request.form.getlist("problems")
        hint_info = request.form["hint_info"]

        update_result = update_contest(contest_id, contest_name, contest_top,
                                       start_date+" "+start_time, end_date+" "+end_time,
                                       frozen_date+ " "+frozen_time,
                                       rate_limit, problems, hint_info)

    # 必要な情報を取得する
    contest_top = get_contest_top(contest_id)
    all_problems = get_all_problem_with_status(session["user_id"], False)
    contest_data = get_contest_data(contest_id)
    hint_json_str = get_contest_hint(contest_id)
    hint_json = json.loads(hint_json_str)
    hint_json_format = json.dumps(hint_json, indent=4).encode("ascii").decode("unicode-escape")

    return render_template("edit_contest.html",
                           session=session["user_id"],
                           update_result=update_result,
                           all_problems=all_problems,
                           contest_top=contest_top,
                           contest=contest_data,
                           hint_json_str=hint_json_format)


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
@route_contest.route(base_url + "/contest/<path:contest_id>", methods=["GET", "POST"])
def contest_view(contest_id):
    # レート更新
    if "update_rate" in request.form.keys() and is_admin(session["user_id"]):
        update_contest_rate(contest_id)
        return redirect(base_url + "/contest_list")

    # ヒント開封
    if "hint_open" in request.form.keys():
        open_hint(contest_id, request.form["hint_open"], session["user_id"])
        return redirect(base_url + "/contest/" + contest_id)

    ranking_data, submission_data = get_ranking_data(contest_id)
    contest_top = markdown2.markdown(get_contest_top(contest_id), extras=['fenced-code-blocks'])
    contest_data = get_contest_data(contest_id)
    problem_list = get_contest_problems(contest_id, session["user_id"])
    hint_info_list = get_hint_data(contest_id, session["user_id"])

    # コンテストが始まっているか
    start_time = datetime.strptime(contest_data.start_time, "%Y-%m-%d %H:%M:%S")
    if (datetime.now() < start_time) and (not is_admin(session["user_id"])):
        problem_list = {}

    return render_template("contest.html",
                           session=session["user_id"],
                           contest_data=contest_data,
                           contest_top=Markup(contest_top),
                           ranking_list=ranking_data,
                           submission_data=submission_data,
                           is_admin=is_admin(session["user_id"]),
                           problem_list=problem_list,
                           hint_info_list=hint_info_list)


