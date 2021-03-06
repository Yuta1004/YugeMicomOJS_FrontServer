import docker
import os
import sqlite3
from server import socketio
from collections import Counter
from gevent.threadpool import ThreadPoolExecutor
from configparser import ConfigParser
from server import config_file

# プログラミング言語と拡張子の対応表
lang_to_extension = {
    "Python3": ".py",
    "Java": ".java",
    "C": ".c",
    "C++": ".cpp"
}

# スレッドプール
executor = ThreadPoolExecutor(max_workers=int(config_file["system"]["max_worker"]))


def judge_code(submission_id):
    """提出されたコードをジャッジする

    Args:
        submission_id (str) : 提出ID

    Returns:
        None
    """

    # ジャッジ開始
    start_judge(submission_id)

    # 問題ID取得
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    problem_id, lang = (cur.execute("SELECT problem_id, lang FROM submission WHERE id = ?",
                             (submission_id, )).fetchone())
    cur.close()
    connect.close()

    # Dockerについていろいろ
    image_name = config_file["docker"]["image_name"]
    env = {"LD_LIBRARY_PATH": "/usr/local/lib:/usr/lib:/usr/local/lib64:/usr/lib64"}
    commands = ["judge-program", lang, "3"]

    # 必要ディレクトリ/ファイルをマウントさせる為の準備
    io_dir = os.path.abspath(".") + "/server/IOData/" + problem_id + "/"
    code_path = os.path.abspath(".") + "/server/Submission/" + submission_id + ".txt"
    info_dict_path = os.path.abspath(".") + "/info_dict.json"
    volumes = {
        io_dir: {
            "bind": "/tmp/judge/io/",
            "mode": "ro"
        },
        code_path: {
            "bind": "/tmp/judge/src/Main" + lang_to_extension[lang],
            "mode": "ro"
        },
        io_dir + "test_case.json": {
            "bind": "/tmp/judge/test_case.json",
            "mode": "ro"
        },
        info_dict_path: {
            "bind": "/tmp/judge/info_dict.json",
            "mode": "ro"
        }
    }

    # ジャッジ
    client = docker.from_env()
    judge_result = client.containers.run(image_name, commands, remove=True, volumes=volumes).decode()

    # スコア取り出し
    judge_result = judge_result.split("`resultend`\n")
    score = int(judge_result[1].replace("\n", ""))
    judge_result = judge_result[0]

    # 判定取り出し
    judge_list = []
    for line in judge_result.split("\n")[:-1]:
        judge_list.append(line.split("`n`")[1])

    if judge_result == "":
        judge_list = ["IE"]

    # 全体の判定を決める
    judge_counter = Counter(judge_list)
    judge_status = judge_counter.most_common()[0][0]
    if judge_status == "AC" and len(judge_list) != judge_counter["AC"]:
        judge_status = judge_counter.most_common()[1][0]

    # 実行時間の最大値を求める
    max_exec_time = -1.0
    for line in judge_result.split("\n")[:-1]:
        exec_time = -1.0
        if line.split("`n`")[2] != "timeout":
            exec_time= float(line.split("`n`")[2])
        max_exec_time = max(exec_time, max_exec_time)

    # TLEの時の実行時間
    if judge_status == "TLE":
        max_exec_time = -1.0

    # 提出データ更新
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    sql = """
          UPDATE submission
          SET status = (SELECT id FROM status WHERE name = ?), detail = ?,
              score = ?, exec_time = ?
          WHERE id = ?
          """
    cur.execute(sql, (judge_status, judge_result.replace("\n", "`;`"), score,
                      max_exec_time, submission_id))
    connect.commit()

    cur.close()
    connect.close()

    # ジャッジ終了
    finish_judge(submission_id, judge_status)


def add_judge_job(submission_id):
    """ジャッジジョブ追加

    Args:
        submission_id (str) : 提出ID

    Returns:
        None
    """
    # ステータス変更
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("UPDATE submission SET status = 0 WHERE id = ?", (submission_id, ))
    connect.commit()
    cur.close()
    connect.close()

    socketio.emit("update_judge_status", (submission_id, "WJ"))
    executor.submit(judge_code, submission_id)


def start_judge(submission_id):
    """ジャッジ開始時に呼ぶ！

    Args:
        submission_id (str) : 提出ID

    Returns:
        None
    """

    # ステータス変更
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    cur.execute("UPDATE submission SET status = -1 WHERE id = ?", (submission_id, ))
    connect.commit()
    cur.close()
    connect.close()

    socketio.emit("update_judge_status", (submission_id, "SJ"))


def finish_judge(submission_id, judge_status):
    """ジャッジ終了時に呼ぶ!

    Args:
        submission_id (str) : 提出ID
        judge_status (str) : ジャッジステータス

    Returns:
        None
    """

    socketio.emit("update_judge_status", (submission_id, judge_status))

