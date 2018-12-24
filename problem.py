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
