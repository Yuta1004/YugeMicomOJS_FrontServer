import os
from configparser import ConfigParser
from server import config_file


def get_file_check(password, path):
    if password != config_file["system"]["password"]:
        return False

    if not os.path.exists(path):
        return False

    return True


def get_code(submission_id, password):
    if not get_file_check(password, "./server/Submission/" + submission_id + ".txt"):
        return ""


    with open("./server/Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        return f.read()


def get_iodata(problem_id, password):
    if not get_file_check(password, "./server/IOData/" + problem_id + ".json"):
        return ""

    with open("./server/IOData/" + problem_id + ".json", "r", encoding="utf-8") as f:
        return f.read()

