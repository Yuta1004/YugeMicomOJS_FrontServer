import sqlite3


class SubmissionInfo:
    def __init__(self, submission_id, problem_id, problem_name, user_id, date, status):
        self.id = submission_id
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.user_id = user_id
        self.date = date
        self.status = status


def get_submission_data(user_id, problem_id):
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    # SQL
    sql_base = "SELECT submission.id, problem.id, problem.name, submission.user_id, submission.date, status.name \
                FROM submission, status \
                INNER JOIN problem ON submission.problem_id = problem.id \
                WHERE submission.status = status.id"

    sql_base_sort = " ORDER BY submission.date DESC"

    # user_id/problem_idに"all"が指定された場合には条件から除外する
    if user_id != "all" and problem_id != "all":
        cur.execute(sql_base  + " AND user_id=? AND problem_id=?" + sql_base_sort,
                    (user_id, problem_id))
    elif user_id != "all":
        cur.execute(sql_base + " AND user_id=?" + sql_base_sort,
                    (user_id, ))
    elif problem_id != "all":
        cur.execute(sql_base + " AND problem_id=?" + sql_base_sort,
                    (problem_id, ))
    else:
        cur.execute(sql_base + sql_base_sort)

    submission_data = []
    for data in cur.fetchall():
        submission_data.append(SubmissionInfo(data[0], data[1], data[2],
                                              data[3], data[4], data[5]))

    cur.close()
    connect.close()

    return submission_data