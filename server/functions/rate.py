import math
import sqlite3


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
    ac_score = math.log(ac_num ** 0.5) + 1
    rank_score = math.log(rank ** 0.2) + 1
    return score * ac_score / rank_score


def cal_contest_rate(contest_id):
    """コンテスト単レートを計算して返す

    Args:
        contest_id (str) : コンテストID

    Returns:
        rate_values(dict) : キー=ユーザID、要素=レートの辞書
    """

    sql = """
          SELECT user_id, MAX(score), ac_num, MAX(submission_time)
          FROM (
                SELECT submission.user_id AS user_id, problem.scoring AS score,
                       MIN(strftime(\"%s\", submission.date) - strftime(\"%s\", contest.start_time)) AS submission_time,
                       SUM(submission.status == 6) AS ac_num
                FROM submission, problem, contest.contest AS contest
                LEFT OUTER JOIN status ON submission.status = status.id
                WHERE contest.id = ? AND contest.start_time <= submission.date AND submission.date <= contest.end_time AND
                      submission.problem_id = problem.id AND contest.problems LIKE (\"%\" || problem.id || \"%\")
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

def update_rate(contest_id):
    """指定IDのコンテストのレート情報を更新する

    Args:
        contest_id (str) : コンテストID

    Returns:
        None
    """

    # レート計算
    rate_values = cal_contest_rate(contest_id)

    # DB記録
    connect = sqlite3.connect("./server/DB/rate.db")
    cur = connect.cursor()
    for user_id, rate in rate_values.items():
        cur.execute("REPLACE INTO single_rate VALUES(?, ?, ?)",
                    (user_id, contest_id, rate))
    connect.commit()
    cur.close()
    connect.close()

