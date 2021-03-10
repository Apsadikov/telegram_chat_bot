import db

database = db.init_database_connection()


def get_current_question(user_id):
    sql = "SELECT current_question_id, lab_id FROM progress WHERE is_finished = false AND user_id = (%s) LIMIT 1"
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    return result[0]


def set_next_question(user_id, lab_id, current_question_id):
    sql = "SELECT id FROM question WHERE lab_id = (%s) ORDER BY created_at ASC"
    value = [lab_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    questions = cursor.fetchall()
    current_question_position = -1
    for i in range(0, len(questions)):
        if questions[i][0] == current_question_id:
            current_question_position = i
    if current_question_position + 1 == len(questions):
        sql = "UPDATE progress SET is_finished = true WHERE lab_id = (%s) AND user_id = (%s)"
        value = [lab_id, user_id]
        cursor = database.cursor()
        cursor.execute(sql, value)
        database.commit()
        return True
    else:
        sql = "UPDATE progress SET current_question_id = %s WHERE lab_id = (%s) AND user_id = (%s)"
        values = [questions[current_question_position + 1][0], lab_id, user_id]
        cursor = database.cursor()
        cursor.execute(sql, values)
        database.commit()
        return False
