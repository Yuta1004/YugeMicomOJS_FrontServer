import sqlite3
from datetime import datetime
import markdown2
import os
from pathlib import Path
import uuid
import json


def add_problem(problem_name, scoring, open_date, open_time, problem_body, score_data, lang_rest):
    """問題追加処理

    Args:
        problem_name (str) : 問題名
        scoring (int) : 配点
        open_time (str) : 問題公開時間[xxxx-xx-xx xx:xx]
        problem_body (str) : 問題文、Markdown形式
        score_data (str) : 部分点データ、Json形式
        lang_rest (list) : 言語縛り

    Returns:
        bool : 問題追加に成功した場合はTrue
        problem_id (str) : 問題ID
    """

    # 入力ミスならreturn
    if problem_name == "" or scoring == "" or open_date == "" or open_time == "" \
            or problem_body == "" or score_data == "":
        return False

    problem_id = str(uuid.uuid4())
    os.mkdir("./server/IOData/" + problem_id)
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()

    # 問題文保存
    with open("./server/Problem/" + problem_id+ ".md", "w", encoding="utf-8") as f:
        f.write(problem_body)

    # 部分点データ保存
    with open("./server/IOData/" + problem_id + "/test_case.json", "w", encoding="utf-8") as f:
        score_data = json.loads(score_data)
        f.write(json.dumps(score_data))

    # DB更新
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("INSERT INTO problem VALUES(?, ?, ?, DATETIME(?), ?)",
                (problem_id, problem_name, scoring, open_date + " " + open_time, ";".join(lang_rest) + ";"))
    connect.commit()
    cur.close()
    connect.close()

    return True, problem_id


def update_problem(problem_id, problem_name, scoring, open_date, open_time, problem_body, test_case_data, lang_rest):
    """問題更新処理

    Args:
        problem_id (str) : 問題ID
        problem_name (str) : 問題名
        scoring (int) : 配点
        open_time (str) : 問題公開時間[xxxx-xx-xx xx:xx]
        problem_body (str) : 問題文、Markdown形式
        test_case_data (str) : テストケースデータ、Json形式
        lang_rest (list) : 言語縛り

    Returns:
        bool : 問題更新に成功した場合はTrue
    """

    # 入力ミスならreturn
    if problem_name == "" or scoring == "" or open_date == "" or open_time == "" \
            or problem_body == "" or test_case_data == "":
        return False

    # 問題文保存
    with open("./server/Problem/" + problem_id+ ".md", "w", encoding="utf-8") as f:
        f.write(problem_body)

    # 入出力データ保存
    with open("./server/IOData/" + problem_id + "/test_case.json", "w", encoding="utf-8") as f:
        test_case_data = json.loads(test_case_data)
        f.write(json.dumps(test_case_data))

    sql = """
          UPDATE problem
          SET name = ?, scoring = ?, open_time = DATETIME(?), lang_rest = ?
          WHERE id = ?
          """

    # DB更新
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute(sql, (problem_name, scoring, open_date + " " + open_time, ";".join(lang_rest), problem_id))
    connect.commit()
    cur.close()
    connect.close()

    return True


def save_io_file(problem_id, files):
    """POSTされた入出力ファイルを保存する

    Args:
        problem_id (str) : 問題ID
        files (flask.requests.files) : リクエストのファイル一覧

    Returns:
        None
    """

    # 保存パス
    save_path = "./server/IOData/" + problem_id + "/"
    io_name_list = ["input", "output"]

    # ファイル保存, input -> output
    for form_name in io_name_list:
        os.makedirs(save_path + form_name, exist_ok=True)
        upload_files = files.getlist(form_name)

        # 含まれる全てのファイルを保存
        for file_obj in upload_files:
            if file_obj.filename[-4:-1] + file_obj.filename[-1] == ".txt":
                file_obj.save(save_path + form_name + "/" + file_obj.filename)


def rm_io_file(problem_id, input_list=None, output_list=None):
    """指定された入出力ファイルを削除する

    Args:
        problem_id (str) : 問題ID
        input_list (list) : 削除する入力ファイルのリスト
        output_list (list) : 削除する出力ファイルのリスト

    Returns:
        None
    """

    # 保存パス
    io_data_path = "./server/IOData/" + problem_id + "/"
    io_list = {"input/": input_list, "output/": output_list}

    # ファイル保存, input -> output
    for dir_name, file_name_list in io_list.items():
        # 含まれる全てのファイルを削除
        for file_name in file_name_list:
            os.remove(io_data_path + dir_name + file_name + ".txt")


class ProblemInfo:
    """問題情報を扱うデータクラス"""

    def __init__(self, _id, name, scoring, open_time, lang_rest, status=None):
        """コンストラクタ

        Args:
            _id (str) : 問題ID
            name (str) : 問題名
            scoring (int) : 配点
            open_time (str) : 公開時間[xxxx-xx-xx xx:xx]
            lang_rest (list) : 言語縛り
            status (str) : ジャッジステータス、指定しない場合はNone

        Returns:
            None
        """

        self.id = _id
        self.name = name
        self.scoring = scoring
        self.open_time = open_time
        self.status = status
        self.lang_rest = lang_rest


def get_all_problem_with_status(user_id, refine_time=True):
    """問題一覧をジャッジステータスと一緒ににして返す

    Args:
        user_id (str) : ユーザID
        refine_time (bool) : 公開時間による縛りを有効にするか

    Returns:
        all_problem (list) : ProblemInfoのリスト
    """

    sql = """
          SELECT problem.id, problem.name, problem.scoring, problem.open_time, problem.lang_rest, IFNULL(submission.status_name, "未提出")
          FROM problem
          LEFT OUTER JOIN (
                SELECT submission.problem_id AS problem_id, max(submission.status), status.name AS status_name
                FROM problem, submission, status
                WHERE problem.id = submission.problem_id AND submission.user_id = ? AND submission.status = status.id
                GROUP BY problem.id
          ) submission ON problem.id = submission.problem_id
          WHERE problem.open_time <= datetime(\"now\", \"+9 hours\")
          ORDER BY problem.scoring
          """

    # 時間で絞り込みをかけるかどうか
    if not refine_time:
        sql = sql.replace("WHERE problem.open_time <= datetime(\"now\", \"+9 hours\")", "")

    # SQL実行
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute(sql, (user_id, ));

    all_problem = []
    for problem in cur.fetchall():
        print(problem[-1])
        all_problem.append(ProblemInfo(*problem[:-2], problem[-2].split(";"), problem[-1]))

    cur.close()
    connect.close()

    return all_problem


def get_problem_data(problem_id):
    """指定IDの問題情報を返す

    Args:
        problem_id (str) : コンテストID

    Returns:
        problem_data (ProblemInfo): コンテスト情報
    """

    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    result = cur.execute("SELECT * FROM problem WHERE id=?", (problem_id, ))
    result = result.fetchone()
    problem_data = ProblemInfo(*result[:-1], result[-1].split(";"))
    cur.close()
    connect.close()

    return problem_data


def get_input_file_list(problem_id):
    """指定IDの入力ファイル一覧を返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        list : 入力ファイルのリスト
    """

    path_obj = Path("./server/IOData/" + problem_id + "/input/")
    return list(path_obj.glob("*"))


def get_output_file_list(problem_id):
    """指定IDの出力ファイル一覧を返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        list : 出力ファイルのリスト
    """

    path_obj = Path("./server/IOData/" + problem_id + "/output/")
    return list(path_obj.glob("*"))


def get_io_file_list(problem_id):
    """指定IDの入出力ファイル一覧を返す

    Args:
        problem_id (str) : 問題ID

    Returns:
        dict : keyに[input], [output]をもつ辞書
    """

    return {"input": get_input_file_list(problem_id),
            "output": get_output_file_list(problem_id)}

