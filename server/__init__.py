from flask import Flask
from flask_bootstrap import Bootstrap
from configparser import ConfigParser

# Config
config_file = ConfigParser()
config_file.read("config.ini")

# Settings
base_url = "/yuge_micom_ojs"
no_login_ok_url = ["/login", "/register", "/get_submission_code", "/get_iodata"]

# Flask
app = Flask(__name__, static_url_path='/yuge_micom_ojs/static')
app.config["SECRET_KEY"] = config_file["system"]["password"]
bootstrap = Bootstrap(app)

# View
from server.views.route_auth import route_auth
from server.views.route_contest import route_contest
from server.views.route_error import route_error
from server.views.route_judge_process import route_judge_process
from server.views.route_problem import route_problem
from server.views.route_submission import route_submission
from server.views.route_top import route_top
from server.views.route_user import route_user

app.register_blueprint(route_auth)
app.register_blueprint(route_contest)
app.register_blueprint(route_error)
app.register_blueprint(route_judge_process)
app.register_blueprint(route_problem)
app.register_blueprint(route_submission)
app.register_blueprint(route_top)
app.register_blueprint(route_user)


