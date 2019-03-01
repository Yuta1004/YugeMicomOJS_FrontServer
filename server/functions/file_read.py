import os
from configparser import ConfigParser
from server import config_file


def get_code(submission_id):
    """提出コードを返す

    Args:
        submission_id (str) : 提出ID

    Return:
        str : コード
    """

    if not os.path.exists("./server/Submission/" + submission_id + ".txt"):
        return ""

    with open("./server/Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        return f.read()


def get_test_case_data(problem_id):
    """テストケースデータを返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        str : テストケースデータ
    """

    if not os.path.exists("./server/IOData/" + problem_id + "/test_case.json"):
        return ""

    with open("./server/IOData/" + problem_id + "/test_case.json", "r", encoding="utf-8") as f:
        return f.read()


def get_problem_body(problem_id):
    """問題文を返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        str : 問題文、Markdown形式
    """

    if not os.path.exists("./server/Problem/" + problem_id + ".md"):
        return ""

    with open("./server/Problem/" + problem_id + ".md", "r", encoding="utf-8") as f:
        return f.read()

