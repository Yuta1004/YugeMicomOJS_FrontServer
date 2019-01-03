import sqlite3
from datetime import datetime
import markdown2
import os
import uuid
import json


def add_problem(problem_name, scoring, open_date, open_time, problem_body, io_data):
    # 入力ミスならreturn
    if problem_name == "" or scoring == 0 or open_date == "" or open_time == "" \
            or problem_body == "" or io_data == "":
        return False

    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    # 問題文保存
    problem_id = str(uuid.uuid4())
    with open("Problem/" + problem_id+ ".md", "w", encoding="utf-8") as f:
        f.write(problem_body)

    # 入出力データ保存
    with open("IOData/" + problem_id + ".json", "w", encoding="utf-8") as f:
        io_data = json.loads(io_data)
        io_data["problem_id"] = problem_id
        f.write(json.dumps(io_data))

    # DB追加
    cur.execute("INSERT INTO problem VALUES(?, ?, ?, ?)",
                (problem_id, problem_name, scoring, open_date + " " + open_time))
    connect.commit()
    cur.close()
    connect.close()

    return True


class ProblemInfo:
    def __init__(self, _id, name, scoring, status):
        self.id = _id
        self.name = name
        self.scoring = scoring
        self.status = status


def get_all_problem(user_id):
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    sql = """
          SELECT problem.id, problem.name, problem.scoring, IFNULL(submission.status_name, "未提出")
          FROM problem
          LEFT OUTER JOIN (
                SELECT submission.problem_id AS problem_id, max(submission.status), status.name AS status_name
                FROM problem, submission, status
                WHERE problem.id = submission.problem_id AND submission.user_id = ? AND submission.status = status.id
                GROUP BY problem.id
          ) submission ON problem.id = submission.problem_id
          WHERE problem.open_time <= datetime(\"now\", \"+9 hours\")
          """

    cur.execute(sql, (user_id, ));

    all_problem = []
    for problem in cur.fetchall():
        all_problem.append(ProblemInfo(problem[0], problem[1],
                                       problem[2], problem[3]))

    cur.close()
    connect.close()

    return all_problem


def get_problem_body(problem_id):
    if not os.path.exists("Problem/" + problem_id + ".md"):
        return None

    problem_body = ""
    with open("Problem/" + problem_id + ".md") as f:
        problem_body = f.read()

    return markdown2.markdown(problem_body, extras=['fenced-code-blocks'])

