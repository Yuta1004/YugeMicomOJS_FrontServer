import sqlite3

class UserInfo:
    def __init__(self, _id, name, open_code):
        self.id = _id
        self.name = name
        self.open_code = open_code


def get_user_data(user_id):
    connect = sqlite3.connect("DB/user.db")
    cur = connect.cursor()

    sql = "SELECT auth_info.id, auth_info.name, settings.open_code \
           FROM auth_info \
           INNER JOIN settings ON auth_info.id = settings.id \
           WHERE auth_info.id = ?"

    result = cur.execute(sql, (user_id, )).fetchall()
    if len(result) != 1:
        return None

    cur.close()
    connect.close()

    result = result[0]
    return UserInfo(result[0], result[1], True if result[2] == 1 else False)


def update_user_data(user_id, user_name, open_code):
    connect = sqlite3.connect("DB/user.db")
    cur = connect.cursor()

    cur.execute("UPDATE auth_info SET name = ? WHERE id = ?",
                (user_name, user_id))
    connect.commit()

    cur.execute("UPDATE settings SET open_code = ? WHERE id = ?",
                (open_code, user_id))
    connect.commit()

    cur.close()
    connect.close()
