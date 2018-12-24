import sqlite3

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
    cur.execute("SELECT * FROM contest");
    for contest in cur.fetchall():
        all_contest.append(ContestInfo(contest[0],
                                       contest[1],
                                       contest[2],
                                       contest[3]))
    return all_contest

