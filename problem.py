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

