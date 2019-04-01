import math
import sqlite3
from collections import OrderedDict
from server.functions.contest import get_contest_data


def cal_rate(max_score, ac_num, rank):
    """単レート計算

    Args:
        max_score (int) : コンテスト中の最高問題得点
        ac_num (int) : AC数
        rank (int) : 順位

    Returns:
        float : 単レート
    """

    score = max_score * math.log(max_score ** 0.3)
    ac_score = math.log(ac_num ** 0.1) + 1
    rank_score = math.log(rank ** 0.1) + 1
    return score * ac_score / rank_score


def cal_contest_rate(contest_id):
    """コンテスト単レートを計算して返す

    Args:
        contest_id (str) : コンテストID

    Returns:
        rate_values(dict) : キー=ユーザID、要素=レートの辞書
    """

    sql = """
          SELECT user_id, MAX(score), COUNT(user_id), MAX(submission_time), total_rate
          FROM (
                SELECT submission.user_id AS user_id, MAX(submission.score) AS score,
                       MIN(strftime(\"%s\", submission.date) - strftime(\"%s\", contest.start_time)) AS submission_time,
                       MAX(rate.total_rate) AS total_rate
                FROM submission, problem, contest.contest AS contest, rate.rate AS rate
                LEFT OUTER JOIN status ON submission.status = status.id
                WHERE contest.id = ? AND contest.start_time <= submission.date AND submission.date <= contest.end_time AND
                      submission.problem_id = problem.id AND contest.problems LIKE (\"%\" || problem.id || \"%\") AND
                      submission.score > 0 AND rate.user_id = submission.user_id
                GROUP BY submission.problem_id, submission.user_id
                ) submission_data, contest.contest
          WHERE contest.id = ? AND contest.rate_limit > total_rate
          GROUP BY user_id
          ORDER BY SUM(score) DESC, MAX(submission_time) ASC
          """

    # 必要な情報をDBから取得
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    cur.execute("ATTACH \"./server/DB/rate.db\" AS rate")
    fetch_result = cur.execute(sql, (contest_id, contest_id)).fetchall()
    cur.close()
    connect.close()

    # 得点帯ごとにまとめる
    group_by_score = {}
    for data in fetch_result:
        if data[1] not in group_by_score:
            group_by_score[data[1]] = []
        group_by_score[data[1]].append(data)

    # レート計算
    rate_values = {}
    rank = 1
    for score in group_by_score.keys():
        for user_info in group_by_score[score]:
            rate_values[user_info[0]] = cal_rate(*user_info[1:3], rank)
            rank += 1
        rank += len(group_by_score[score]) * 1.5

    return rate_values


def cal_user_rate(user_id):
    """指定ユーザのレートを計算する

    Args:
        user_id (str) : ユーザID

    Returns:
        rate (float) : レート
    """

    # DB接続
    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")

    # BEST
    sql = """
          SELECT SUM(single_rate)
          FROM rate
          WHERE user_id = ?
          ORDER BY single_rate
          LIMIT 10
          """
    best = cur.execute(sql, (user_id, )).fetchone()[0]

    # RECENT
    sql = """
          SELECT SUM(single_rate)
          FROM rate, contest
          WHERE user_id = ? AND contest_id = contest.id
          ORDER BY contest.end_time
          LIMIT 10
          """
    recent = cur.execute(sql, (user_id, )).fetchone()[0]
    cur.close()
    connect.close()

    return best * 0.07 + recent * 0.03


def update_contest_rate(contest_id, with_update_user = True):
    """指定IDのコンテストの単レート情報を更新する

    Args:
        contest_id (str) : コンテストID

    Returns:
        None
    """

    # レート計算
    rate_values = cal_contest_rate(contest_id)

    # コンテスト単レート更新
    update_sql = """
                REPLACE INTO rate VALUES(?, ?, ?, (
                    SELECT total_rate
                    FROM rate
                    WHERE user_id = ?
                ))
                """

    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    for user_id, rate in rate_values.items():
        cur.execute(update_sql, (user_id, contest_id, rate, user_id))
    connect.commit()
    cur.close()
    connect.close()

    # ユーザレート更新
    if with_update_user:
        for user_id in rate_values.keys():
            update_user_rate(user_id, contest_id)


def update_user_rate(user_id, contest_id):
    """指定ユーザのレート情報を更新する

    Args:
        user_id (str) : ユーザID
        contest_id (str) : コンテストID

    Returns:
        None
    """

    # レート計算
    rate = cal_user_rate(user_id)

    update_sql = """
                 REPLACE INTO rate VALUES(?, ?, (
                    SELECT single_rate
                    FROM rate
                    WHERE user_id = ?
                 ), ?)
                 """
    # 更新
    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    cur.execute(update_sql, (user_id, contest_id, user_id, rate))
    connect.commit()
    cur.close()
    connect.close()


def get_user_rate_data(user_id):
    """指定ユーザのレートの情報を返す

    Args:
        user_id (str) : ユーザID

    Returns:
        rate (float) : レート情報
    """

    # DBからデータ取得
    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    rate = cur.execute("SELECT total_rate FROM rate WHERE user_id = ?",
                               (user_id, )).fetchone()
    cur.close()
    connect.close()

    # 返す
    if rate is None:
        return 0.0
    else:
        return rate[0]


def get_user_rate_trans_data(user_id):
    """指定ユーザのレート推移を渡す

    Args:
        user_id (str) : ユーザID

    Returns:
        dict (str : int) : キーにコンテスト名、値にその時点でのレート
    """

    # データ取得
    fetch_sql = """
                SELECT contest.name, rate.total_rate
                FROM contest, rate
                WHERE rate.user_id = ? AND rate.contest_id = contest.id AND rate.total_rate <> 0.0
                ORDER BY (
                    SELECT end_time
                    FROM contest
                    WHERE contest.id = rate.contest_id
                )
                """

    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    fetch_result = cur.execute(fetch_sql, (user_id, )).fetchall()
    cur.close()
    connect.close()

    # 辞書型に変換
    rate_trans_info = OrderedDict()
    for info in fetch_result:
        rate_trans_info[info[0]] = info[1]

    return rate_trans_info

