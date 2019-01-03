import sqlite3
import uuid
from judge import add_judge_job


class SubmissionInfo:
    def __init__(self, submission_id, problem_id, problem_name, user_id, date, lang, status, detail):
        self.id = submission_id
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.user_id = user_id
        self.date = date
        self.lang = lang
        self.status = status
        self.detail = detail


def get_submission_data(user_id, problem_id):
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    # SQL
    sql_base = "SELECT submission.id, problem.id, problem.name, submission.user_id, submission.date, submission.lang, status.name, submission.detail \
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
                                              data[3], data[4], data[5],
                                              data[6], data[7]))

    cur.close()
    connect.close()

    return submission_data


class SubmissionDetail:
    def __init__(self, status, err_msg):
        self.status = status
        self.err_msg = err_msg

def get_data_for_submission_page(submission_id):
    # 問題ID、ユーザID取得
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()
    fetch_result = cur.execute("SELECT problem_id, user_id FROM submission WHERE id = ?",
                               (submission_id, )).fetchone()
    problem_id = fetch_result[0]
    user_id = fetch_result[1]
    cur.close()
    connect.close()

    # 提出データ取得
    submission_data = get_submission_data(user_id, problem_id)[0]

    # 詳細情報パース
    detail = submission_data.detail.split(";")
    detail = [item.split("`") for item in detail]

    detail_data = {}
    for elem in detail[:-1]:
        detail_data[elem[0]] = SubmissionDetail(elem[1],
                                                elem[2].replace("$", "\n").replace("/tmp/judge/src", "/path/to/code"))
    submission_data.detail = detail_data

    # 提出コード取得
    with open("Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        submission_code = f.read()

    return submission_data, submission_code

def save_submission(user_id, problem_id, lang, code):
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    submission_id = str(uuid.uuid4())

    # 提出コード保存
    with open("Submission/" + submission_id + ".txt", "w", encoding="utf-8") as f:
        f.write(code)

    # 提出記録
    cur.execute("INSERT INTO submission VALUES(?, ?, ?, datetime(CURRENT_TIMESTAMP, \"+9 hours\"), ?, 0, \"\")",
                (submission_id, user_id, problem_id, lang))
    connect.commit()

    cur.close()
    connect.close()

    # 判定ジョブを追加
    add_judge_job(submission_id, problem_id)

