import os
import sqlite3
import uuid
from datetime import datetime
from server.functions.judge import add_judge_job

class SubmissionInfo:
    """提出情報を扱うデータクラス"""

    def __init__(self, submission_id, problem_id, problem_name, open_time,
                 user_id, user_name, date, lang, status, detail, score, exec_time):
        """コンストラクタ

        Args:
            submission_id (str) : 提出ID
            problem_id (str) : 問題ID
            problem_name (str) : 問題名
            open_time (str) : 問題公開時間[xxxx-xx-xx xx:xx]
            user_id (str) : ユーザID
            user_name (str) : ユーザ名
            date (str) : 提出時間[xxxx-xx-xx xx:xx]
            lang (str) : 提出言語
            status (str) : ジャッジステータス
            detail (SubmissonDetail) : 実行詳細
            score (str) : スコア
            exec_time (float) : コード実行時間

        Returns:
            None
        """

        self.id = submission_id
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.open_time = datetime.strptime(open_time, "%Y-%m-%d %H:%M:%S")
        self.user_id = user_id
        self.user_name = user_name
        self.date = date
        self.lang = lang
        self.status = status
        self.detail = detail
        self.score = score
        self.exec_time = float(exec_time)

        if self.exec_time >= 0:
            self.exec_time *= 1000
            self.exec_time = int(self.exec_time)


def get_submission_data(user_id, problem_id):
    """指定ユーザID・問題IDで絞り込んだ提出情報一覧を返す

    Description:
        user_id / problem_idに[all]を指定した場合は絞り込みが無効になる

    Args:
        user_id (str) : 絞り込みをかけるユーザID
        problem_id (str) : 絞り込みをかける問題ID

    Returns:
        submission_data (list) : SubmissionInfoのリスト
    """

    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/user.db\" AS user")

    # SQL
    sql_base =  """
                SELECT submission.id, problem.id, problem.name, problem.open_time,
                       submission.user_id, user.auth_info.name, submission.date,
                       submission.lang, status.name, submission.detail, submission.score, submission.exec_time\
                FROM submission, status, user.auth_info \
                INNER JOIN problem ON submission.problem_id = problem.id \
                WHERE submission.status = status.id AND submission.user_id = user.auth_info.id
                """

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
        submission_data.append(SubmissionInfo(*data))

    cur.close()
    connect.close()

    return submission_data


class SubmissionDetail:
    """提出情報詳細を扱うデータクラス"""

    def __init__(self, test_case_name, status, exec_time, err_msg):
        """コンストラクタ

        Args:
            test_case_name (str) : テストケース名
            status (str) : ジャッジステータス
            err_msg (str) : 実行詳細
            exec_time (float) : 実行時間

        Returns:
            None
        """

        self.test_case_name = test_case_name
        self.status = status
        self.err_msg = err_msg
        self.exec_time = float(exec_time)

        if self.exec_time >= 0:
            self.exec_time *= 1000
            self.exec_time = int(self.exec_time)


def get_data_for_submission_page(user_id, submission_id):
    """提出詳細ページを描画するために必要な情報を返す

    Args:
        user_id (str) : ユーザID
        submission_id (str) : 提出ID

    Returns:
        submission_data (SubmissionInfo) : 提出情報
        submission_code (str) : 提出コード
        do_open_code (bool) : 提出コード公開設定
    """

    # 提出詳細取得
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/user.db\" AS user")

    sql = """
          SELECT submission.id, problem.id, problem.name, problem.open_time,
                 submission.user_id, user.auth_info.name, submission.date,
                 submission.lang, status.name, submission.detail, submission.score,
                 submission.exec_time, problem.open_time
          FROM submission, status, user.auth_info
          INNER JOIN problem ON submission.problem_id = problem.id
          WHERE submission.status = status.id AND submission.id = ? AND user.auth_info.id = submission.user_id
          """
    fetch_result = cur.execute(sql, (submission_id, )).fetchone()
    submission_data = SubmissionInfo(*fetch_result[:12])

    # 必要情報取得
    submission_user_id = fetch_result[4]
    open_time = fetch_result[12]
    cur.close()
    connect.close()

    # 詳細情報パース
    detail = submission_data.detail.split("`;`")
    detail = [item.split("`n`") for item in detail]
    detail_data = {}
    for idx, elem in enumerate(detail[:-1]):
        if len(elem) == 5:
            if elem[2] == "timeout":
                elem[2] = -1.0
            detail_data[str(idx)] = SubmissionDetail(elem[0],   # テストケース名
                                                     elem[1],   # ジャッジステータス
                                                     elem[2],   # 実行時間
                                                     elem[3].replace("`n2`", "\n").replace("/tmp/judge/src", "/path/to/code"))
        else:
            detail_data[str(idx)] = SubmissionDetail(elem[0],   # テストケース名
                                                     elem[1],   # ジャッジステータス
                                                     0.0,       # 実行時間
                                                     elem[2].replace("`n2`", "\n").replace("/tmp/judge/src", "/path/to/code"))

    submission_data.detail = detail_data

    # 提出コード取得
    with open("./server/Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        submission_code = f.read()

    # 提出コード公開設定取得
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()
    open_code = cur.execute("SELECT open_code FROM settings WHERE id = ?", (submission_user_id, )).fetchone()[0]
    time_format = "%Y-%m-%d %H:%M:%S"
    do_open_code = (open_code == 1 and datetime.strptime(open_time, time_format) <= datetime.now()) \
                        or user_id == submission_user_id

    return submission_data, submission_code, do_open_code


def save_submission(user_id, problem_id, lang, code):
    """提出情報を保存してジャッジジョブを追加する

    Args:
        user_id (str) : ユーザID
        problem_id (str) : 問題ID
        lang (str) : 提出言語
        code (str) : 提出コード

    Returns:
        None
    """

    # 提出コード保存
    submission_id = str(uuid.uuid4())
    with open("./server/Submission/" + submission_id + ".txt", "w", encoding="utf-8") as f:
        f.write(code)

    # 提出記録
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("INSERT INTO submission VALUES(?, ?, ?, datetime(CURRENT_TIMESTAMP, \"+9 hours\"), ?, 0, \"\", 0, 0.0)",
                (submission_id, user_id, problem_id, lang))
    connect.commit()
    cur.close()
    connect.close()

    # 判定ジョブを追加
    add_judge_job(submission_id)


def remove_submission(submission_id):
    """指定IDの提出を削除する

    Args:
        Submission_id (str) : 提出ID

    Returns:
        None
    """

    # DBから削除
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("DELETE FROM submission WHERE id = ?", (submission_id, ))
    connect.commit()
    cur.close()
    connect.close()

    # 提出コード削除
    os.remove("./server/Submission/" + submission_id + ".txt")
