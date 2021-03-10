import db

database = db.init_database_connection()


def create_answer(user_id, lab_id, answer):
    sql = "INSERT INTO answer (user_id, lab_id, answer) VALUES (%s, %s, %s)"
    values = [user_id, lab_id, answer]
    cursor = database.cursor()
    cursor.execute(sql, values)
    database.commit()


def get_answers(user_id, lab_id):
    sql = "SELECT answer FROM answer WHERE user_id = (%s) AND lab_id = (%s)"
    values = [user_id, lab_id]
    cursor = database.cursor()
    cursor.execute(sql, values)
    return cursor.fetchall()
