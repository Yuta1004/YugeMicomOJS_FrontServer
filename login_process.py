import bcrypt
import sqlite3

def login(user_id, password):
    if user_id == "" or password == "":
        return False

    connect = sqlite3.connect("DB/user.db")
    cur = connect.cursor()

    # ユーザ検索
    user_search_result = cur.execute("SELECT * FROM auth_info WHERE id = ?",
                                     (user_id, ))
    if len(user_search_result.fetchall()) == 0:
        cur.close()
        connect.close()
        return False

    # 認証
    cur.execute("SELECT password FROM auth_info WHERE id = ?",
                (user_id, ))
    registed_pass = cur.fetchone()[0]

    return bcrypt.checkpw(password.encode(), registed_pass.encode())


def register(user_id, user_name, password, password_conf):
    connect = sqlite3.connect("DB/user.db")
    cur = connect.cursor()

    if password != password_conf:
        return False

    user_search_result = cur.execute("SELECT * FROM auth_info WHERE id=?",
                                     (user_id, ))
    if len(user_search_result.fetchall()) > 0:
        cur.close()
        connect.close()
        return False

    # ソルト生成 -> パスワードのHASH化
    gen_salt = bcrypt.gensalt(rounds=12, prefix=b'2a')
    hash_password = bcrypt.hashpw(password.encode(), gen_salt)

    # ユーザ追加
    cur.execute("INSERT INTO auth_info VALUES(?, ?, ?)",
                (user_id, user_name, hash_password.decode()))
    connect.commit()

    cur.close()
    connect.close()

    return True