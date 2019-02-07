from flask import request, Blueprint
from server.functions.file_read import get_code, get_iodata
from server import base_url

route_judge_process = Blueprint(__name__, "judge_process")

# ジャッジプロセスが提出コードをダウンロードするときにアクセスするところ
@route_judge_process.route(base_url + "/get_submission_code/<path:submission_id>")
def get_submission_code(submission_id):
    if "password" not in request.headers:
        return "HTTP HEADER ERROR"

    return get_code(submission_id, request.headers["password"])


# ジャッジプロセスが入出力データをダウンロードするときにアクセスするところ
@route_judge_process.route(base_url + "/get_iodata/<path:problem_id>")
def get_iodata_route(problem_id):
    if "password" not in request.headers:
        return "HTTP HEADER ERROR"

    return get_iodata(problem_id, request.headers["password"])


