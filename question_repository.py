import db

database = db.init_database_connection()


def create_question(lab_id, text, is_question_without_answer_options):
    sql = "INSERT INTO question (lab_id, text, is_question_without_answer_options) VALUES (%s, %s, %s)"
    value = [lab_id, text, is_question_without_answer_options]
    cursor = database.cursor()
    cursor.execute(sql, value)
    database.commit()
    return cursor.lastrowid


def get_question(question_id):
    sql = "SELECT text, is_question_without_answer_options FROM question WHERE id = (%s) LIMIT 1"
    value = [question_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    question = cursor.fetchall()[0]
    answer_options = None
    if question[1]:
        sql = "SELECT text FROM answer_option WHERE question_id = (%s)"
        value = [question_id]
        cursor = database.cursor()
        cursor.execute(sql, value)
        answer_options = cursor.fetchall()
    return [question, answer_options]
