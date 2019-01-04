import docker
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from configparser import ConfigParser


# Config
config_file = ConfigParser()
config_file.read("config.ini")

# スレッドプール
executor = ThreadPoolExecutor(max_workers=int(config_file["system"]["max_worker"]))

def judge_code(submission_id):
    # 問題ID取得
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()
    problem_id = cur.execute("SELECT problem_id FROM submission WHERE id = ?",
                             (submission_id, )).fetchone()[0]
    cur.close()
    connect.close()

    client = docker.from_env()

    image_name = config_file["docker"]["image_name"]
    env = {"LD_LIBRARY_PATH": "/usr/local/lib:/usr/lib:/usr/local/lib64:/usr/lib64"}
    commands = [
        "judge-program",
        config_file["system"]["server_url"],
        config_file["system"]["password"],
        submission_id,
        problem_id
    ]

    judge_result = client.containers.run(image_name, commands, remove=True, environment=env)

    # 判定取り出し
    judge_list = []
    for line in judge_result.decode().split("\n")[:-1]:
        judge_list.append(line.split("`")[1])

    if judge_result.decode() == "":
        judge_list = ["IE"]

    # 全体の判定を決める
    judge_counter = Counter(judge_list)
    judge_status = judge_counter.most_common()[0][0]
    if judge_status == "AC" and len(judge_list) != judge_counter["AC"]:
        judge_status = judge_counter.most_common()[1][0]

    # 提出データ更新
    connect = sqlite3.connect("DB/problem.db")
    cur = connect.cursor()

    judge_status_id = cur.execute("SELECT id FROM status WHERE name = ?", (judge_status, )).fetchone()[0]
    sql = "UPDATE submission SET status = ?, detail = ? WHERE id = ?"
    cur.execute(sql, (judge_status_id, judge_result.decode().replace("\n", ";"), submission_id))
    connect.commit()

    cur.close()
    connect.close()


def add_judge_job(submission_id):
    executor.submit(judge_code, submission_id)

