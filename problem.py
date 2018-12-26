import sqlite3
from datetime import datetime

class ProblemInfo:
    def __init__(self, _id, name, scoring, open_time):
        self.id = _id
        self.name = name
        self.scoring = scoring
        self.open_time = open_time


def get_all_problem():
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    cur.execute("SELECT * FROM problem");

    all_problem = []
    time_format = "%Y/%m/%d/%H/%M" 
    for problem in cur.fetchall():
        all_problem.append(ProblemInfo(problem[0],
                                   problem[1],
                                   problem[2],
                                   datetime.strptime(problem[3], time_format)))

    # 公開しても良いものだけ抽出
    now = datetime.now()
    all_problem = [problem for problem in all_problem if problem.open_time <= now]

    return all_problem


class SubmissionInfo:
    def __init__(self, submission_id, user_id, problem_id, date):
        self.id = submission_id
        self.user_id = user_id
        self.problem_id = problem_id
        self.date = date


def get_submission_data(user_id, problem_id):
    connect = sqlite3.connect("DB/submission.db")
    cur = connect.cursor()

    # user_id/problem_idに"all"が指定された場合には条件から除外する
    if user_id != "all" and problem_id != "all":
        cur.execute("SELECT * FROM submission WHERE user_id=? AND problem_id=?",
                    (user_id, problem_id))
    elif user_id != "all":
        cur.execute("SELECT * FROM submission WHERE user_id=?",
                    (user_id, ))
    elif problem_id != "all":
        cur.execute("SELECT * FROM submission WHERE problem_id=?",
                    (problem_id, ))
    else:
        cur.execute("SELECT * FROM submission")

    submission_data = []
    for data in cur.fetchall():
        submission_data.append(SubmissionInfo(data[0],
                                              data[1],
                                              data[2],
                                              data[3]))

    return submission_data

