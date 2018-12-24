import sqlite3

class Problem:
    def __init__(self, _id, name, contest_id, scoring):
        self.id = _id
        self.name = name
        self.contest_id = contest_id
        self.scoring = scoring


def get_all_problem():
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    cur.execute("SELECT * FROM problem");

    all_problem = []
    for problem in cur.fetchall():
        all_problem.append(Problem(problem[0],
                                   problem[1],
                                   problem[2],
                                   problem[3]))

    return all_problem
