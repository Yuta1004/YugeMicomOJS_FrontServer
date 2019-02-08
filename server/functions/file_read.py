import os
from configparser import ConfigParser
from server import config_file


def get_file_check(password, path):
    """ファイルが存在するかを返す(パスワード認証付き)

    Description:
        ジャッジコンテナからの正常なアクセスであるかどうかを認証する必要がある

    Args:
        password (str) : パスワード
        path (str) : ファイルパス

    Return:
        bool : ファイルが存在する場合はTrue
    """

    if password != config_file["system"]["password"]:
        return False

    if not os.path.exists(path):
        return False

    return True


def get_code(submission_id, password):
    """提出コードを返す

    Description:
        ジャッジコンテナ以外からのアクセスは無効にする

    Args:
        submission_id (str) : 提出ID
        password (str) : パスワード

    Return:
        str : コード
    """

    if not get_file_check(password, "./server/Submission/" + submission_id + ".txt"):
        return ""


    with open("./server/Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        return f.read()


def get_iodata(problem_id, password):
    """入出力データを返す

    Description:
        ジャッジコンテナ以外からのアクセスは無効にする

    Args:
        problem_id (str) : 問題ID
        password (str) : パスワード

    Returns:
        str : 入出力データ
    """

    if not get_file_check(password, "./server/IOData/" + problem_id + ".json"):
        return ""

    with open("./server/IOData/" + problem_id + ".json", "r", encoding="utf-8") as f:
        return f.read()


def get_problem_body(problem_id):
    """問題文を返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        str : 問題文、HTML形式
    """

    if not os.path.exists("./server/Problem/" + problem_id + ".md"):
        return ""

    problem_body = ""
    with open("./server/Problem/" + problem_id + ".md", "r", encoding="utf-8") as f:
        return f.read()


