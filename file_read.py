import os


def get_code(submission_id, password):
    if password != os.environ["JUDGE_SYSTEM_PASSWORD"]:
        return ""

    if not os.path.exists("Submission/" + submission_id + ".txt"):
        return ""

    with open("Submission/" + submission_id + ".txt", "r", encoding="utf-8") as f:
        return f.read()

