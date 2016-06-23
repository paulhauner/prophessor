import pymysql
from local_settings import PHAB_DB_HOST, PHAB_DB_USER, PHAB_DB_PASSWORD


class Database():
    def connect(self):
        return pymysql.connect(
            host=PHAB_DB_HOST,
            user=PHAB_DB_USER,
            password=PHAB_DB_PASSWORD,
            cursorclass=pymysql.cursors.DictCursor
        )

    def disconnect(self, connection):
        connection.close()

db = Database()