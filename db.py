from mysql.connector import connect, Error


def init_database_connection():
    return connect(
        host="localhost",
        user="root",
        password="1234",
        database="lab"
    )
