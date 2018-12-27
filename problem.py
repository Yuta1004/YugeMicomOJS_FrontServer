import sqlite3
from datetime import datetime
import markdown2
import os

class ProblemInfo:
    def __init__(self, _id, name, scoring, open_time):
        self.id = _id
        self.name = name
        self.scoring = scoring
        self.open_time = open_time


def get_all_problem():
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    cur.execute("SELECT * FROM problem WHERE open_time <= datetime(\"now\", \"+9 hours\")");

    all_problem = []
    for problem in cur.fetchall():
        all_problem.append(ProblemInfo(problem[0],
                                       problem[1],
                                       problem[2],
                                       problem[3]))

    cur.close()
    connect.close()

    return all_problem


class SubmissionInfo:
    def __init__(self, submission_id, problem_id, problem_name, user_id, date):
        self.id = submission_id
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.user_id = user_id
        self.date = date


def get_submission_data(user_id, problem_id):
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    sql_base = "SELECT submission.id, problem.id, problem.name, submission.user_id, submission.date \
                FROM submission \
                INNER JOIN problem ON submission.problem_id = problem.id"

    # user_id/problem_idに"all"が指定された場合には条件から除外する
    if user_id != "all" and problem_id != "all":
        cur.execute(sql_base  + " WHERE user_id=? AND problem_id=? ORDER BY submission.date DESC",
                    (user_id, problem_id))
    elif user_id != "all":
        cur.execute(sql_base + " WHERE user_id=? ORDER BY submission.date DESC",
                    (user_id, ))
    elif problem_id != "all":
        cur.execute(sql_base + " WHERE problem_id=? ORDER BY submission.date DESC",
                    (problem_id, ))
    else:
        cur.execute(sql_base + " ORDER BY submission.date DESC")

    submission_data = []
    for data in cur.fetchall():
        submission_data.append(SubmissionInfo(data[0],
                                              data[1],
                                              data[2],
                                              data[3],
                                              data[4]))

    cur.close()
    connect.close()

    return submission_data


def get_problem_body(problem_id):
    if not os.path.exists("Problem/" + problem_id + ".md"):
        return None

    problem_body = ""
    with open("Problem/" + problem_id + ".md") as f:
        problem_body = f.read()

    return markdown2.markdown(problem_body, extras=['fenced-code-blocks'])

