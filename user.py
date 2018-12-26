import sqlite3

class UserInfo:
    def __init__(self, _id, name, open_code):
        self.id = _id
        self.name = name
        self.open_code = open_code


def get_user_info(user_id):
    connect = sqlite3.connect("DB/user.db")
    cur = connect.cursor()

    sql = "SELECT auth_info.id, auth_info.name, settings.open_code \
           FROM auth_info \
           INNER JOIN settings ON auth_info.id = settings.id \
           WHERE auth_info.id = ?"

    result = cur.execute(sql, (user_id, )).fetchall()
    if len(result) != 1:
        return None

    result = result[0]
    return UserInfo(result[0], result[1], True if result[2] == 1 else False)

