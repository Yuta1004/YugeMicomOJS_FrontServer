from flask import Flask, session, request, redirect, render_template
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from configparser import ConfigParser
from server.functions.user import is_admin

# Config
config_file = ConfigParser()
config_file.read("config.ini")

# Settings
base_url = "/yuge_micom_ojs"
no_login_ok_url = ["/login", "/register", "/get_submission_code", "/get_iodata"]

# Flask
app = Flask(__name__, static_url_path='/yuge_micom_ojs/static')
app.config["SECRET_KEY"] = config_file["system"]["password"]
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024     # 4MB
socketio = SocketIO(app, async_mode=None)
bootstrap = Bootstrap(app)


# BeforeRequestRoute
@app.before_request
def before_request():
    if "user_id" not in session.keys():
       session["user_id"] = None

    # ログインする必要があるか判断
    enough_login = True
    for url in no_login_ok_url:
        if url in request.url:
            enough_login = False

    if enough_login and session["user_id"] is None:
        return redirect(base_url + "/login")

    # ログイン制限
    login_rest = False
    if session["user_id"] is not None:
        # 特定のユーザを制限
        if session["user_id"] in config_file["user"]["login_rest_users"]:
            login_rest = True

        # 管理者以外制限
        if config_file["user"]["login_rest_users"] == "all" and not is_admin(session["user_id"]):
            login_rest = True


    if login_rest:
        if "/logout" not in request.url and "/login_rest" not in request.url:
            return redirect(base_url + "/login_rest")


# LoginRestUser
@app.route(base_url + "/login_rest")
def login_rest():
    return render_template("login_rest.html",
                           session=session["user_id"])



# ErrorHandler
@app.errorhandler(404)
def error_404_notfound(error):
    return render_template("404.html",
                           session=session["user_id"])


# View
from server.views.route_auth import route_auth
from server.views.route_admin import route_admin
from server.views.route_contest import route_contest
from server.views.route_problem import route_problem
from server.views.route_submission import route_submission
from server.views.route_top import route_top
from server.views.route_user import route_user

app.register_blueprint(route_auth)
app.register_blueprint(route_admin)
app.register_blueprint(route_contest)
app.register_blueprint(route_problem)
app.register_blueprint(route_submission)
app.register_blueprint(route_top)
app.register_blueprint(route_user)


