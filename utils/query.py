from collections import namedtuple
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor
from django.db import connection

try:
    '''
    SETIAP MAU PUSH UNCOMMENT CONNECTION KE RAILWAY & COMMENT CONNECTION LOCAL
    '''
    # connection = psycopg2.connect(user="postgres",
    #                     password='TBaCPVaBPEmMTXrJ1RDd',
    #                     host="containers-us-west-2.railway.app",
    #                     port="6346",
    #                     database="railway")
    connection = psycopg2.connect(user="postgres",
                        password="postgres",
                        host="localhost",
                        port="5432",
                        database="babadu")
    #                     password="annisa123",
    #                     host="127.0.0.1",
    #                     port="5433",
    #                     database="postgres")

    # Create a cursor to perform database operations
    connection.autocommit = True
    cursor = connection.cursor()
except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)


def map_cursor(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [dict(row) for row in cursor.fetchall()]


def query(query_str: str):
    hasil = []
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SET SEARCH_PATH TO babadu")
        try:
            cursor.execute(query_str)

            if query_str.strip().upper().startswith("SELECT"):
                # Kalau tidak error, return hasil SELECT
                hasil = map_cursor(cursor)
            else:
                # Kalau tidak error, return jumlah row yang termodifikasi oleh INSERT, UPDATE, DELETE
                hasil = cursor.rowcount
                connection.commit()
        except Exception as e:
            # Error yang tidak diketahui
            hasil = e

    return hasil