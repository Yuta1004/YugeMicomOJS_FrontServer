import os


def get_file_check(password, path):
    if password != os.environ["JUDGE_SYSTEM_PASSWORD"]:
        return False

    if not os.path.exists(path):
        return False

    return True


def get_code(submission_id, password):
    if not get_file_check(password, "Submission/" + submission_id + ".txt"):
        return ""


    with open("Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        return f.read()


def get_iodata(problem_id, password):
    if not get_file_check(password, "IOData/" + problem_id + ".json"):
        return ""

    with open("IOData/" + problem_id + ".json", "r", encoding="utf-8") as f:
        return f.read()

