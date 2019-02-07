import sqlite3
import bcrypt
from server.functions.login_process import login

class UserInfo:
    def __init__(self, _id, name, position, open_code):
        self.id = _id
        self.name = name
        self.position = position
        self.open_code = open_code


def get_user_data(user_id):
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()

    sql = "SELECT auth_info.id, auth_info.name, auth_info.position, settings.open_code \
           FROM auth_info \
           INNER JOIN settings ON auth_info.id = settings.id \
           WHERE auth_info.id = ?"

    result = cur.execute(sql, (user_id, )).fetchall()
    if len(result) != 1:
        return None

    cur.close()
    connect.close()

    result = result[0]
    return UserInfo(result[0], result[1], result[2], result[3] == 1)


def update_user_data(user_id, user_name, open_code):
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()

    if user_name == "":
        return False

    # 更新処理
    cur.execute("UPDATE auth_info SET name = ? WHERE id = ?",
                (user_name, user_id))
    cur.execute("UPDATE settings SET open_code = ? WHERE id = ?",
                (open_code, user_id))
    connect.commit()

    cur.close()
    connect.close()

    return True


def change_password(user_id, old_pass, new_pass, new_pass_conf):
    if new_pass != new_pass_conf or not login(user_id, old_pass):
        return False

    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()

    # 半角英数8文字以上
    if len(new_pass) < 8 or not new_pass.encode('utf-8').isalnum():
        return False

    # ソルト生成 -> パスワードのHASH化
    gen_salt = bcrypt.gensalt(rounds=12, prefix=b'2a')
    hash_password = bcrypt.hashpw(new_pass.encode(), gen_salt)

    # パスワード変更
    cur.execute("UPDATE auth_info SET password = ? WHERE id = ?",
                (hash_password.decode(), user_id))
    connect.commit()

    cur.close()
    connect.close()

    return True


def is_admin(user_id):
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()

    position = cur.execute("SELECT position FROM auth_info WHERE id = ?",
                           (user_id, )).fetchone()[0]
    cur.close()
    connect.close()

    return position == "admin"
