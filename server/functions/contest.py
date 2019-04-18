import sqlite3
from datetime import datetime
from server.functions.problem import ProblemInfo
from server.functions.file_read import get_contest_hint
import uuid
import json


def add_contest(contest_name, contest_top, start_time, end_time, rate_limit, problems, hint_info):
    """ コンテストをDBに追加する

    Args:
        contest_name (str) : コンテスト名
        contest_top (str) : コンテスト情報(Markdown形式)
        start_time (str) : 開始時刻[xxxx-xx-xx xx:xx]
        end_time (str) : 終了時刻[xxxx-xx-xx xx:xx]
        rate_limit (int) : レート付与上限
        problems (list) : 問題IDのリスト
        hint_info (str:json) : ヒント情報

    Returns:
        bool : 正常に追加されればTrue
    """

    # 入力チェック
    try:
        json.loads(hint_info)
    except json.JSONDecodeError:
        return False

    if contest_name == "" or contest_top == "" or start_time == "" or\
        end_time == "" or rate_limit is None or problems is None or hint_info == "":
        return False

    # コンテスト追加
    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()
    contest_id = str(uuid.uuid4())
    cur.execute("INSERT INTO contest VALUES(?, ?, DATETIME(?), DATETIME(?), ?, ?)",
                (contest_id, contest_name, start_time, end_time, ";".join(problems), rate_limit))
    connect.commit()
    cur.close()
    connect.close()

    # コンテスト情報保存
    with open("./server/ContestPage/" + contest_id + ".md", "w", encoding="utf-8") as f:
        f.write(contest_top)

    # ヒント情報
    with open("./server/Hint/" + contest_id + ".json", "w", encoding="utf-8") as f:
        f.write(json.dumps(json.loads(hint_info)))

    return True


def update_contest(contest_id, contest_name, contest_top, start_time, end_time, rate_limit, problems, hint_info):
    """ 指定IDのコンテスト情報を更新する

    Args:
        contest_id (str) : コンテストID
        contest_name (str) : コンテスト名
        contest_top (str) ; コンテスト情報(Markdown形式)
        start_time (str) : 開始時刻[xxxx-xx-xx xx:xx]
        end_time (str) : 終了時刻[xxxx-xx-xx xx:xx]
        rate_limit (int) : レート付与上限
        problems (list) : 問題IDのリスト
        hint_info (str:json) : ヒント情報

    Returns:
        bool : 正常に追加されればTrue
    """

    # 入力チェック
    try:
        json.loads(hint_info)
    except json.JSONDecodeError:
        return False

    if contest_id == "" or contest_name == "" or contest_top == "" or start_time == "" or \
            end_time == "" or rate_limit is None or problems is None or hint_info == "":
        return False

    sql = """
          UPDATE contest
          SET name = ?, start_time = DATETIME(?), end_time = DATETIME(?), problems = ?, rate_limit = ?
          WHERE id = ?
          """

    # 更新
    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()
    cur.execute(sql, (contest_name, start_time, end_time, ";".join(problems), rate_limit, contest_id))
    connect.commit()
    cur.close()
    connect.close()

    # コンテスト情報保存
    with open("./server/ContestPage/" + contest_id + ".md", "w", encoding="utf-8") as f:
        f.write(contest_top)

    # ヒント情報
    with open("./server/Hint/" + contest_id + ".json", "w", encoding="utf-8") as f:
        f.write(json.dumps(json.loads(hint_info)))

    return True


class ContestInfo:
    """コンテスト情報を扱うデータクラス"""

    def __init__(self, _id, name, start, end, rate_limit, problems):
        """コンストラクタ

        Args:
            _id (str) : コンテストID
            name (str) : コンテスト名
            start (str) : 開始時刻[xxxx-xx-xx xx:xx]
            end (str) : 終了時刻[xxxx-xx-xx xx:xx]
            rate_limit (int) : レート付与上限
            problems (list) : コンテスト対象の問題IDのリスト

        Returns:
            None
        """

        self.id = _id
        self.name = name
        self.start_time = start
        self.end_time = end
        self.rate_limit = rate_limit
        self.problems = problems


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
                                       datetime.strptime(contest[3], time_format),
                                       int(contest[5]),
                                       contest[4].split(";")))
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
    result = cur.execute("SELECT * FROM contest WHERE id=?", (contest_id, )).fetchone()
    contest_data = ContestInfo(*result[:4], int(result[5]), result[4].split(";"))
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
          SELECT problem.id, problem.name, problem.scoring, problem.open_time, problem.lang_rest, IFNULL(submission.status_name, "未提出")
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
          ORDER BY problem.scoring
    """
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    result = cur.execute(sql, (user_id, contest_id))

    problems = []
    for elem in result.fetchall():
        problems.append(ProblemInfo(*elem[:-2], elem[-2].split(";"), elem[-1]))

    cur.close()
    connect.close()

    return problems


class RankingInfo:
    """ランキングの個々データを扱うデータクラス"""

    def __init__(self, rank, user_id, user_name, score, submission_time):
        """コンストラクタ

        Args:
            rank (int) : 順位
            user_id (str) : ユーザID
            user_name (str) : ユーザ名
            score (int) : スコア
            submission_time (str) : 最終有効提出時刻[xx:xx:xx]

        Returns:
            None
        """

        self.rank = rank
        self.user_id = user_id
        self.user_name = user_name
        self.score = score
        self.submission_time = str(submission_time // 3600).zfill(2) + ":" + \
                               str(submission_time % 3600 // 60).zfill(2) + ":" + \
                               str(submission_time % 60).zfill(2)



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
          SELECT user_id, user.auth_info.name, SUM(score), MAX(submission_time)
          FROM (
                SELECT submission.user_id AS user_id, MAX(submission.score) AS score,
                       MIN(strftime(\"%s\", submission.date) - strftime(\"%s\", contest.start_time)) AS submission_time
                FROM submission, problem, contest.contest AS contest
                LEFT OUTER JOIN status ON submission.status = status.id
                WHERE contest.id = ? AND contest.start_time <= submission.date AND submission.date <= contest.end_time AND submission.score > 0 AND
                      submission.problem_id = problem.id AND contest.problems LIKE (\"%\" || problem.id || \"%\")
                GROUP BY problem.id, submission.user_id
                ) submission_data, user.auth_info
          WHERE user.auth_info.id = user_id
          GROUP BY user_id
          ORDER BY SUM(score) DESC, MAX(submission_time) ASC
          """
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("ATTACH \"./server/DB/contest.db\" AS contest")
    cur.execute("ATTACH \"./server/DB/user.db\" AS user")
    result = cur.execute(sql, (contest_id, )).fetchall()

    # ヒント開封データ取得
    sql = """
          SELECT user_id, SUM(score)
          FROM contest.hint_open, contest.contest AS contest
          WHERE contest_id = ? AND contest.id = ? AND open_time < contest.end_time
          GROUP BY user_id
          """
    hint_open_info = dict(cur.execute(sql, (contest_id, contest_id)).fetchall())

    # 減点処理
    ranking_member = []
    for elem in result:
        score = elem[2]
        if elem[0] in hint_open_info.keys():
            score -= hint_open_info[elem[0]]
        ranking_member.append([elem[0], elem[1], max(10, score), elem[3]])

    # 降順ソート -> 集計
    ranking_member = sorted(ranking_member, key=lambda x: x[2], reverse=True)
    ranking_list = []
    for rank, elem in enumerate(ranking_member):
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


class HintInfo:
    """ヒント情報を扱うデータクラス"""

    def __init__(self, contest_id, hint_id, user_id, title, score, open_flag, body):
        """コンストラクタ

        Args:
            contest_id (str) : コンテストID
            hint_id (str) : ヒントID
            user_id (str) : ユーザID
            title (str) : タイトル
            score (int) : 減点
            open_flag (bool) : 開封されているかどうか
            body (str) : ヒント情報

        Returns:
            None
        """

        self.contest_id = contest_id
        self.hint_id = hint_id
        self.user_id = user_id
        self.title = title
        self.score = score
        self.open_flag = open_flag
        self.body = body


def get_hint_data(contest_id, user_id):
    """あるユーザのコンテストでのヒント情報一覧を返す

    Args:
        contest_id (str) : コンテストID
        user_id (str) : ユーザID

    Returns:
        list (HintInfo) : ヒント情報のリスト
    """

    sql = """
          SELECT DISTINCT contest_id, hint_id, user_id
          FROM hint_open, contest
          WHERE contest_id = ? AND contest.id = ? AND user_id = ? AND
                (open_time < contest.end_time OR open_time IS NULL)
          """

    # DB接続 -> ヒント開封情報取得
    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()
    sql_result = cur.execute(sql, (contest_id, contest_id, user_id)).fetchall()
    cur.close()
    connect.close()

    # ヒント情報取得
    hint_dict = get_contest_hint(contest_id)
    hint_dict = json.loads(hint_dict)["Hint"]

    # ヒント情報 + 開封情報
    for elem in sql_result:
        hint_dict[elem[1]]["user_id"] = elem[2]
        hint_dict[elem[1]]["open_flag"] = True

    # to HintInfo
    hint_info_list = []
    for hint_id in hint_dict.keys():
        if "user_id" not in hint_dict[hint_id].keys():
            hint_dict[hint_id]["user_id"] = ""
            hint_dict[hint_id]["open_flag"] = False

        hint_info = HintInfo(contest_id,
                             hint_id,
                             hint_dict[hint_id]["user_id"],
                             hint_dict[hint_id]["title"],
                             hint_dict[hint_id]["score"],
                             hint_dict[hint_id]["open_flag"],
                             hint_dict[hint_id]["body"])
        hint_info_list.append(hint_info)


    return hint_info_list


def open_hint(contest_id, hint_id, user_id):
    """ヒント開封情報を記録する

    Args:
        contest_id (str) : コンテストID
        hint_id (str) : ヒントID
        user_id (str) : ユーザID

    Returns:
        None
    """

    # ヒントスコア取得
    hint_dict = get_contest_hint(contest_id)
    hint_score = json.loads(hint_dict)["Hint"][hint_id]["score"]

    sql = "INSERT INTO hint_open VALUES(?, ?, ?, ?, datetime(CURRENT_TIMESTAMP, \"+9 hours\"))"

    # DB接続 -> 記録
    connect = sqlite3.connect("./server/DB/contest.db")
    cur = connect.cursor()
    cur.execute(sql, (contest_id, hint_id, user_id, hint_score))
    connect.commit()
    cur.close()
    connect.close()

