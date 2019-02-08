import sqlite3
from datetime import datetime
import markdown2
import os
import uuid
import json


def add_problem(problem_name, scoring, open_date, open_time, problem_body, io_data):
    """問題追加処理

    Args:
        problem_name (str) : 問題名
        scoring (int) : 配点
        open_time (str) : 問題公開時間[xxxx-xx-xx xx:xx]
        problem_body (str) : 問題文、Markdown形式
        io_data (str) : 入出力データ、Json形式

    Returns:
        bool : 問題追加に成功した場合はTrue
    """

    # 入力ミスならreturn
    if problem_name == "" or scoring == "" or open_date == "" or open_time == "" \
            or problem_body == "" or io_data == "":
        return False

    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()

    # 問題文保存
    problem_id = str(uuid.uuid4())
    with open("./server/Problem/" + problem_id+ ".md", "w", encoding="utf-8") as f:
        f.write(problem_body)

    # 入出力データ保存
    with open("./server/IOData/" + problem_id + ".json", "w", encoding="utf-8") as f:
        io_data = json.loads(io_data)
        io_data["problem_id"] = problem_id
        f.write(json.dumps(io_data))

    # DB更新
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("INSERT INTO problem VALUES(?, ?, ?, DATETIME(?))",
                (problem_id, problem_name, scoring, open_date + " " + open_time))
    connect.commit()
    cur.close()
    connect.close()

    return True


class ProblemInfo:
    """問題情報を扱うデータクラス"""

    def __init__(self, _id, name, scoring, open_time, status=None):
        """コンストラクタ

        Args:
            _id (str) : 問題ID
            name (str) : 問題名
            scoring (int) : 配点
            open_time (str) : 公開時間[xxxx-xx-xx xx:xx]
            status (str) : ジャッジステータス、指定しない場合はNone

        Returns:
            None
        """

        self.id = _id
        self.name = name
        self.scoring = scoring
        self.open_time = open_time
        self.status = status


def get_all_problem_with_status(user_id, refine_time=True):
    """問題一覧をジャッジステータスと一緒ににして返す

    Args:
        user_id (str) : ユーザID
        refine_time (bool) : 公開時間による縛りを有効にするか

    Returns:
        all_problem (list) : ProblemInfoのリスト
    """

    sql = """
          SELECT problem.id, problem.name, problem.scoring, problem.open_time, IFNULL(submission.status_name, "未提出")
          FROM problem
          LEFT OUTER JOIN (
                SELECT submission.problem_id AS problem_id, max(submission.status), status.name AS status_name
                FROM problem, submission, status
                WHERE problem.id = submission.problem_id AND submission.user_id = ? AND submission.status = status.id
                GROUP BY problem.id
          ) submission ON problem.id = submission.problem_id
          WHERE problem.open_time <= datetime(\"now\", \"+9 hours\")
          """

    # 時間で絞り込みをかけるかどうか
    if not refine_time:
        sql = sql.replace("WHERE problem.open_time <= datetime(\"now\", \"+9 hours\")", "")

    # SQL実行
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute(sql, (user_id, ));

    all_problem = []
    for problem in cur.fetchall():
        all_problem.append(ProblemInfo(*problem))

    cur.close()
    connect.close()

    return all_problem


def get_problem_body(problem_id):
    """問題文を返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        str : 問題文、HTML形式
    """

    if not os.path.exists("./server/Problem/" + problem_id + ".md"):
        return None

    problem_body = ""
    with open("./server/Problem/" + problem_id + ".md", "r", encoding="utf-8") as f:
        problem_body = f.read()

    return markdown2.markdown(problem_body, extras=['fenced-code-blocks'])

