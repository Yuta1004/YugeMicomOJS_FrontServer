import math
import sqlite3
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
          SELECT user_id, MAX(score), COUNT(user_id), MAX(submission_time)
          FROM (
                SELECT submission.user_id AS user_id, submission.scoring AS score,
                       MIN(strftime(\"%s\", submission.date) - strftime(\"%s\", contest.start_time)) AS submission_time
                FROM submission, problem, contest.contest AS contest
                LEFT OUTER JOIN status ON submission.status = status.id
                WHERE contest.id = ? AND contest.start_time <= submission.date AND submission.date <= contest.end_time AND
                      submission.problem_id = problem.id AND contest.problems LIKE (\"%\" || problem.id || \"%\") AND submission.status = 6
                GROUP BY submission.problem_id, submission.user_id
                ) submission_data
          GROUP BY user_id
          ORDER BY SUM(score) DESC, MAX(submission_time) ASC
          """

    # 必要な情報をDBから取得
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    fetch_result = cur.execute(sql, (contest_id, )).fetchall()
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
          SELECT SUM(rate)
          FROM single_rate
          WHERE user_id = ?
          ORDER BY rate
          LIMIT 10
          """
    best = cur.execute(sql, (user_id, )).fetchone()[0]

    # RECENT
    sql = """
          SELECT SUM(rate)
          FROM single_rate, contest
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
    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    for user_id, rate in rate_values.items():
        cur.execute("REPLACE INTO single_rate VALUES(?, ?, ?)", (user_id, contest_id, rate))
    connect.commit()
    cur.close()
    connect.close()

    # ユーザレート更新
    if with_update_user:
        for user_id in rate_values.keys():
            update_user_rate(user_id)


def update_user_rate(user_id):
    """指定ユーザのレート情報を更新する

    Args:
        user_id (str) : ユーザID

    Returns:
        None
    """

    # レート計算
    rate = cal_user_rate(user_id)

    # DB記録
    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    cur.execute("REPLACE INTO user_rate VALUES(?, ?)", (user_id, rate))
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
    rate = cur.execute("SELECT rate FROM user_rate WHERE user_id = ?",
                               (user_id, )).fetchone()
    cur.close()
    connect.close()

    # 返す
    if rate is None:
        return 0.0
    else:
        return rate[0]

