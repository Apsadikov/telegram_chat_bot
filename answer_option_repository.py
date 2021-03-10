import db

db = db.init_database_connection()


def create_answer(question_id, answer):
    sql = "INSERT INTO answer_option (text, question_id) VALUES (%s, %s)"
    value = [answer, question_id]
    cursor = db.cursor()
    cursor.execute(sql, value)
    db.commit()
