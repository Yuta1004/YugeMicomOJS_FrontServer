import os
from pathlib import Path
import json
import sqlite3

# 入出力例ファイル一覧取得
io_files = list(Path("./server/IOData/").glob("*.json"))

for io_file in io_files:
    # ディレクトリ作成
    io_dir = str(io_file).split("/")[-1].split(".")[0]
    os.makedirs("./server/IOData/" + io_dir + "/input", exist_ok=True)
    os.makedirs("./server/IOData/" + io_dir + "/output", exist_ok=True)

    # json読み込み
    print(io_file)
    with open(io_file, "r", encoding="utf-8") as f:
        json_data = json.loads(f.read())
    test_case_num = json_data["test_case_size"]

    # 入出力ファイル作成
    for io_type in ["input", "output"]:
        for num in range(test_case_num):
            testcase = json_data[io_type][str(num)]
            file_path = "./server/IOData/" + io_dir + "/" + io_type + "/TestCase_" + str(num) + ".txt"
            with open(file_path, "w", encoding="utf-8") as f:
                for line in testcase:
                    f.write(line + "\n")

    # スコア情報取得
    connect = sqlite3.connect("./server/DB/problem.db")
    cur = connect.cursor()
    score = cur.execute("SELECT scoring FROM problem WHERE id = ?", (io_dir, )).fetchone()[0]
    cur.close()
    connect.close()


    # テストケースファイル作成
    test_case_json = {}
    test_case_json["testcase"] = {}
    test_case_json["testcase"]["NormalTestCase"] = {}
    test_case_json["testcase"]["NormalTestCase"]["score"] = score
    test_case_json["testcase"]["NormalTestCase"]["case_list"] = ["TestCase_" + str(num) for num in range(test_case_num)]
    with open("./server/IOData/" + io_dir + "/test_case.json", "w", encoding="utf-8") as f:
        json.dump(test_case_json, f)

