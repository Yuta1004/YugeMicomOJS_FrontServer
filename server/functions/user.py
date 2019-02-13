import sqlite3
import bcrypt
from server.functions.login_process import login

class UserInfo:
    """ユーザデータを扱うデータクラス"""

    def __init__(self, _id, name, position, open_code):
        """コンストラクタ

        Args:
            _id (str) : ユーザID
            name (str) : ユーザ名/ニックネーム
            position (str) : [admin]で管理者、それ以外は一般ユーザ
            open_code (str) : コード公開設定

        Returns:
            None
        """

        self.id = _id
        self.name = name
        self.position = position
        self.open_code = open_code


def get_user_data(user_id):
    """指定IDのユーザデータを返す

    Args:
        user_id (str) : ユーザID

    Returns:
        UserInfo : ユーザデータ
    """

    sql = "SELECT auth_info.id, auth_info.name, auth_info.position, settings.open_code \
           FROM auth_info \
           INNER JOIN settings ON auth_info.id = settings.id \
           WHERE auth_info.id = ?"

    # データ取得
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()
    result = cur.execute(sql, (user_id, )).fetchall()
    if len(result) != 1:
        return None

    cur.close()
    connect.close()

    result = result[0]
    return UserInfo(result[0], result[1], result[2], result[3] == 1)


def update_user_data(user_id, user_name, open_code):
    """指定IDのユーザデータを更新する

    Args:
        user_id (str) : ユーザID
        user_name (str) : ユーザ名/ニックネーム
        open_code (int) : コード公開設定、1を指定すると公開するになる

    Returns:
        bool : 更新に成功したらTrue
    """
    if user_name == "":
        return False

    # 更新処理
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()
    cur.execute("UPDATE auth_info SET name = ? WHERE id = ?",
                (user_name, user_id))
    cur.execute("UPDATE settings SET open_code = ? WHERE id = ?",
                (open_code, user_id))
    connect.commit()
    cur.close()
    connect.close()

    return True


def change_password(user_id, old_pass, new_pass, new_pass_conf):
    """指定ユーザのパスワードを変更する

    Args:
        user_id (str) : ユーザID
        old_pass (str) : 旧パスワード
        new_pass (str) : 新パスワード
        new_pass_conf (str) : 新パスワード、入力確認用

    Returns:
        bool : 正常に変更されたらTrue
    """

    if new_pass != new_pass_conf or not login(user_id, old_pass):
        return False

    # 半角英数8文字以上
    if len(new_pass) < 8 or not new_pass.encode('utf-8').isalnum():
        return False

    # ソルト生成 -> パスワードのHASH化
    gen_salt = bcrypt.gensalt(rounds=12, prefix=b'2a')
    hash_password = bcrypt.hashpw(new_pass.encode(), gen_salt)

    # パスワード変更
    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()
    cur.execute("UPDATE auth_info SET password = ? WHERE id = ?",
                (hash_password.decode(), user_id))
    connect.commit()
    cur.close()
    connect.close()

    return True


def is_admin(user_id):
    """指定IDのユーザが管理者かどうかを返す

    Args:
        user_id (str) : ユーザID

    Returns:
        bool : 管理者の場合はTtue
    """

    connect = sqlite3.connect("./server/DB/user.db")
    cur = connect.cursor()
    position = cur.execute("SELECT position FROM auth_info WHERE id = ?",
                           (user_id, )).fetchone()[0]
    cur.close()
    connect.close()

    return position == "admin"
