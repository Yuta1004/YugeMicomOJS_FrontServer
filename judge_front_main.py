from flask import Flask, render_template, request, session, redirect, url_for, Markup, abort
from flask_bootstrap import Bootstrap
from configparser import ConfigParser
from login_process import register, login
from user import get_user_data, update_user_data, change_password, is_admin
from problem import get_all_problem, get_problem_body, add_problem
from submission import get_submission_data, save_submission, get_data_for_submission_page
from contest import get_3type_divided_contest, get_contest_problems, get_contest_data, get_ranking_data, add_contest
from file_read import get_code, get_iodata
from judge import add_judge_job

# Config
config_file = ConfigParser()
config_file.read("config.ini")

# Flask
app = Flask(__name__)
app.config["SECRET_KEY"] = config_file["system"]["password"]
bootstrap = Bootstrap(app)

# Other
base_url = "/yuge_micom_ojs"
no_login_ok_url = ["/login", "/register", "/get_submission_code", "/get_iodata"]

#Routes
@app.before_request
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
@app.route(base_url + "/")
def index():
    return render_template("index.html",
                           session=session["user_id"])


# ユーザ登録ページ
@app.route(base_url + "/register", methods=["GET", "POST"])
def register_user():
    if request.method == "GET":
        return render_template("register.html",
                               session=session["user_id"])

    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    password = request.form["password"]
    password_conf = request.form["password_conf"]

    # ユーザ登録
    if register(user_id, user_name, password, password_conf):
        session["user_id"] = user_id
        return redirect("/yuge_micom_ojs")
    else:
        return render_template("register.html",
                               inp_failed="Failed",
                               session=session["user_id"])


# ログインページ
@app.route(base_url + "/login", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login.html",
                               session=session["user_id"])

    user_id = request.form["user_id"]
    password = request.form["password"]

    # 認証
    if login(user_id, password):
        session["user_id"] = user_id
        return redirect(base_url)
    else:
        return render_template("login.html",
                               login_failed="Failed",
                               session=session["user_id"])


# ログアウト(トップページにリダイレクト)
@app.route(base_url + "/logout")
def logout_user():
    session["user_id"] = None
    return redirect(base_url)


# ユーザ設定ページ
@app.route(base_url + "/user_settings", methods=["POST", "GET"])
def user_settings():
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

    return render_template("user_settings.html",
                           user=user_info,
                           update_succeeded=update_succeeded,
                           session=session["user_id"])


# パスワード変更ページ
@app.route(base_url + "/change_password", methods=["POST", "GET"])
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


# 問題追加ページ(管理者のみ)
@app.route(base_url + "/add_problem", methods=["GET", "POST"])
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


# コンテスト追加ページ(管理者のみ)
@app.route(base_url + "/add_contest", methods=["GET", "POST"])
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
@app.route(base_url + "/contest_list")
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
@app.route(base_url + "/contest/<path:contest_id>")
def contest_view(contest_id):
    ranking_data, submission_data = get_ranking_data(contest_id)

    return render_template("contest.html",
                           session=session["user_id"],
                           contest_data=get_contest_data(contest_id),
                           ranking_list=ranking_data,
                           submission_data=submission_data,
                           problem_list=get_contest_problems(contest_id, session["user_id"]))


# 問題一覧表示ページ
@app.route(base_url + "/problem_list")
def problem_list_view():
    now_page = request.args.get("page", 1, type=int)

    return render_template("problem_list.html",
                            session=session["user_id"],
                            now_page=now_page,
                            problem_list=get_all_problem(session["user_id"]))


# 問題情報表示ページ
@app.route(base_url + "/problem/<path:problem_id>", methods=["GET", "POST"])
def problem_view(problem_id):
    # コード提出(POST)
    if request.method == "POST":
        save_submission(session["user_id"], problem_id,
                        request.form["submission_lang"],
                        request.form["submission_code"])

        return redirect(base_url + "/submission_list/all")

    # 問題ページ描画
    problem_body = get_problem_body(problem_id)
    if problem_body is None:
        return abort(404)

    return render_template("problem.html",
                            session=session["user_id"],
                            problem_body=Markup(problem_body))


# 提出一覧表示ページ
@app.route(base_url + "/submission_list/<path:user_id>")
def submission_list_view(user_id):
    now_page = request.args.get("page", 1, type=int)

    return render_template("submission_list.html",
                           session=session["user_id"],
                           now_page=now_page,
                           submission_data=get_submission_data(user_id, "all"))


# 提出情報表示ページ
@app.route(base_url + "/submission/<path:submission_id>", methods=["GET", "POST"])
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


# Routes(FileSend)
# ジャッジプロセスが提出コードをダウンロードするときにアクセスするところ
@app.route(base_url + "/get_submission_code/<path:submission_id>")
def get_submission_code(submission_id):
    if "password" not in request.headers:
        return "HTTP HEADER ERROR"

    return get_code(submission_id, request.headers["password"])


# ジャッジプロセスが入出力データをダウンロードするときにアクセスするところ
@app.route(base_url + "/get_iodata/<path:problem_id>")
def get_iodata_route(problem_id):
    if "password" not in request.headers:
        return "HTTP HEADER ERROR"

    return get_iodata(problem_id, request.headers["password"])


# ErrorHandler
@app.errorhandler(404)
def error_404_notfound(error):
    return render_template("404.html",
                           session=session["user_id"])


if __name__ == '__main__':
    app.run(port=11000)
