import db

database = db.init_database_connection()


def get_answer_spreadsheet_link(lab_id):
    sql = "SELECT answer_spreadsheet_link FROM lab WHERE id = (%s) LIMIT 1"
    value = [lab_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return result[0][0]


def is_lab_exist(lab_id):
    sql = "SELECT * FROM lab WHERE id = (%s) LIMIT 1"
    value = [lab_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return len(result) != 0


def is_user_has_unfinished_labs(user_id):
    sql = "SELECT * FROM progress WHERE user_id = (%s) AND is_finished = 0"
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return len(result) != 0


def is_user_finished_lab(user_id, lab_id):
    sql = "SELECT * FROM progress WHERE user_id = (%s) AND is_finished = 1 AND lab_id = (%s)"
    value = [user_id, lab_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return len(result) != 0


def create_new_lab_for_user(user_id, lab_id):
    sql = "SELECT id, text, is_question_without_answer_options FROM question WHERE lab_id = (%s) ORDER BY created_at ASC LIMIT 1"
    value = [lab_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    current_question_id = result[0][0]
    sql = "INSERT INTO progress (user_id, lab_id, current_question_id) VALUES (%s, %s, %s)"
    values = [user_id, lab_id, current_question_id]
    cursor = database.cursor()
    cursor.execute(sql, values)
    database.commit()


def create_lab():
    sql = "INSERT INTO lab (answer_spreadsheet_link) VALUES (null)"
    cursor = database.cursor()
    cursor.execute(sql)
    database.commit()
    return cursor.lastrowid


def set_answer_spreadsheet_link(lab_id, answer_spreadsheet_link):
    sql = "UPDATE lab SET answer_spreadsheet_link = (%s) WHERE id = (%s)"
    values = [answer_spreadsheet_link, lab_id]
    cursor = database.cursor()
    cursor.execute(sql, values)
    database.commit()
