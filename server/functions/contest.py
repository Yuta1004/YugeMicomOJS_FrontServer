import sqlite3
from datetime import datetime
from server.functions.problem import ProblemInfo
import uuid


def add_contest(contest_name, start_time, end_time, problems):
    """ コンテストをDBに追加する

    Args:
        contest_name (str) : コンテスト名
        start_time (str) : 開始時刻[xxxx-xx-xx xx:xx]
        end_time (str) : 終了時刻[xxxx-xx-xx xx:xx]
        problems (list) : 問題IDのリスト

    Returns:
        bool : 正常に追加されればTrue
    """

    # 入力チェック
    if contest_name == "" or start_time == "" or end_time == "" or problems is None:
        return False

    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()

    # コンテスト追加
    contest_id = str(uuid.uuid4())
    cur.execute("INSERT INTO contest VALUES(?, ?, DATETIME(?), DATETIME(?), ?)",
                (contest_id, contest_name, start_time, end_time, ";".join(problems)))
    connect.commit()
    cur.close()
    connect.close()

    return True


class ContestInfo:
    """コンテスト情報を扱うデータクラス"""

    def __init__(self, _id, name, start, end):
        """コンストラクタ

        Args:
            _id (str) : コンテストID
            name (str) : コンテスト名
            start (str) : 開始時刻[xxxx-xx-xx xx:xx]
            end (str) : 終了時刻[xxxx-xx-xx xx:xx]

        Returns:
            None
        """

        self.id = _id
        self.name = name
        self.start_time = start
        self.end_time = end


def get_all_contest():
    """登録されているコンテスト一覧を返す

    Args:
        None

    Returns:
        all_contest (list) : ContestInfoのリスト
    """
    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()

    all_contest = []
    time_format = "%Y-%m-%d %H:%M:%S"
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
    """開催前・開催中・開催後の3種類にコンテストを分類して返す

    Args:
        None

    Returns:
        past_contest (list) : 開催後のコンテスト、ContestInfoのリスト
        now_contest (list) : 開催中のコンテスト、ContestInfoのリスト
        future_contest (list) : 開催前のコンテスト、ContestInfoのリスト
    """

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
    """指定IDのコンテスト情報を返す

    Args:
        contest_id (str) : コンテストID

    Returns:
        contest_data (ContestInfo): コンテスト情報
    """

    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()

    result = cur.execute("SELECT * FROM contest WHERE id=?", (contest_id, ))
    result = result.fetchone()
    print(result)
    contest_data = ContestInfo(*result[:4])

    cur.close()
    connect.close()

    return contest_data


def get_contest_problems(contest_id, user_id):
    """指定コンテストに含まれる問題一覧と、指定ユーザIDの提出状況を合わせて返す

    Args:
        contest_id (str) : コンテストID
        user_id (str): ユーザID

    Returns:
        problems (list) : ProblemInfoのリスト
    """

    # コンテストに含まれる問題一覧を取得する
    sql = """
          SELECT problem.id, problem.name, problem.scoring, problem.open_time, IFNULL(submission.status_name, "未提出")
          FROM problem
          LEFT OUTER JOIN (
                SELECT submission.problem_id AS problem_id, max(submission.status), status.name AS status_name
                FROM problem, submission, status
                WHERE problem.id = submission.problem_id AND submission.user_id = ? AND submission.status = status.id
                GROUP BY problem.id
          ) submission ON problem.id = submission.problem_id
          WHERE(
                SELECT contest.contest.problems
                FROM contest.contest
                WHERE contest.contest.id=?
          ) LIKE (\"%\" || problem.id || \"%\")
    """
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    result = cur.execute(sql, (user_id, contest_id))

    problems = []
    for elem in result.fetchall():
        problems.append(ProblemInfo(*elem))

    cur.close()
    connect.close()

    return problems


class RankingInfo:
    """ランキングの個々データを扱うデータクラス"""

    def __init__(self, rank, user_id, score, submission_time):
        """コンストラクタ

        Args:
            rank (int) : 順位
            user_id (str) : ユーザID
            score (int) : スコア
            submission_time (str) : 最終有効提出時刻[xxxx-xx-xx xx:xx]

        Returns:
            None
        """

        self.rank = rank
        self.user_id = user_id
        self.score = score
        self.submission_time = submission_time


def get_ranking_data(contest_id):
    """指定コンテストのランキングと提出状況を返す

    Args:
        contest_id (str); コンテストID

    Returns:
        ranking_list (list) : RankingInfoのリスト
        submission_data (dict) : key1 = ユーザID, key2 = 問題ID, item = 提出状況
    """

    # ランキングデータ取得
    sql = """
          SELECT user_id, SUM(score), MAX(submission_time)
          FROM (
                SELECT submission.user_id AS user_id, problem.scoring  AS score,
                       MIN(strftime(\"%s\", submission.date) - strftime(\"%s\", contest.start_time)) AS submission_time
                FROM submission, problem, contest.contest AS contest
                LEFT OUTER JOIN status ON submission.status = status.id
                WHERE contest.id = ? AND contest.start_time <= submission.date AND submission.date <= contest.end_time AND status.name == "AC" AND
                      submission.problem_id = problem.id AND contest.problems LIKE (\"%\" || problem.id || \"%\")
                GROUP BY problem.id, submission.user_id
                ) submission_data
          GROUP BY user_id
          ORDER BY SUM(score) DESC, MAX(submission_time) ASC
          """
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    result = cur.execute(sql, (contest_id, )).fetchall()

    ranking_list = []
    for rank, elem in enumerate(result):
        ranking_list.append(RankingInfo(rank, *elem))

    # 全員の提出状況を取得
    sql = """
          SELECT submission.user_id, submission.problem_id, MAX(submission.status), status.name
          FROM submission, status, (
                SELECT contest.contest.problems AS problems, contest.contest.start_time AS start_time, contest.contest.end_time AS end_time
                FROM contest.contest
                WHERE contest.contest.id = ?
            ) AS contest
          WHERE submission.status = status.id AND contest.problems LIKE (\"%\" || submission.problem_id || \"%\") AND
                    contest.start_time <= submission.date AND submission.date <= contest.end_time
          GROUP BY submission.problem_id, submission.user_id
          """
    result = cur.execute(sql, (contest_id, )).fetchall()

    submission_data = {}
    for line in result:
        if line[0] not in submission_data.keys():
            submission_data[line[0]] = {}
        submission_data[line[0]][line[1]] = line[3]

    cur.close()
    connect.close()

    return ranking_list, submission_data

