import db

database = db.init_database_connection()


def is_user_exist(user_id):
    sql = "SELECT * FROM user WHERE id = (%s) LIMIT 1"
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return len(result) != 0


def create_user(user_id, full_name):
    sql = "INSERT INTO user (id, full_name) VALUES (%s, %s)"
    values = [user_id, full_name]
    cursor = database.cursor()
    cursor.execute(sql, values)
    database.commit()


def get_user_full_name(user_id):
    sql = "SELECT full_name FROM user WHERE id = (%s) LIMIT 1"
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return result[0][0]
