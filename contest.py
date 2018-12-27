import sqlite3
from datetime import datetime
from problem import ProblemInfo

class ContestInfo:
    def __init__(self, _id, name, start, end):
        self.id = _id
        self.name = name
        self.start_time = start
        self.end_time = end


def get_all_contest():
    connect = sqlite3.connect("DB/contest.db")
    cur = connect.cursor()

    all_contest = []
    time_format = "%Y/%m/%d/%H/%M"
    cur.execute("SELECT * FROM contest");
    for contest in cur.fetchall():
        all_contest.append(ContestInfo(contest[0],
                                       contest[1],
                                       datetime.strptime(contest[2], time_format),
                                       datetime.strptime(contest[3], time_format)))

    cur.close()
    connect.close()

    return all_contest


def get_3type_divided_contest():
    now = datetime.now()
    past_contest = []
    now_contest = []
    future_contest = []

    for contest in get_all_contest():
        if contest.start_time <= now <= contest.end_time:
            now_contest.append(contest)

        elif contest.end_time < now:
            past_contest.append(contest)

        else:
            future_contest.append(contest)

    return past_contest, now_contest, future_contest


def get_contest_data(contest_id):
    connect = sqlite3.connect("DB/contest.db")
    cur = connect.cursor()

    result = cur.execute("SELECT * FROM contest WHERE id=?", (contest_id, ))
    result = result.fetchone()
    contest_data = ContestInfo(result[0], result[1], result[2], result[3])

    cur.close()
    connect.close()

    return contest_data


def get_contest_problems(contest_id):
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    # contest.dbをアタッチ
    cur.execute("ATTACH \"DB/contest.db\" AS contest")

    # コンテストに含まれる問題一覧を取得するsql
    sql = """
          SELECT problem.id, problem.name, problem.scoring
          FROM problem
          WHERE(
                SELECT contest.contest.problems
                FROM contest.contest
                WHERE contest.contest.id=?
          ) LIKE (\"%\" || problem.id || \"%\")
          """
    result = cur.execute(sql, (contest_id, ))
    problems = []
    for elem in result.fetchall():
        problems.append(ProblemInfo(elem[0], elem[1], elem[2], ""))

    cur.close()
    connect.close()

    return problems

