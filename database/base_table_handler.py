from database.database import Database
import datetime
import psycopg2 

class BaseTableHandler:

    def __init__(self, table, select_sql=None):
        self.table = table
        if select_sql:
            self.select_sql = select_sql
        else:
            self.select_sql = f"SELECT * FROM {table}"
        return

    def set(self, key, value):
        raise NotImplementedError  # To be defined by every command

    def remove(self, key):
        raise NotImplementedError  # To be defined by every command

    def get(self, key):
        raise NotImplementedError  # To be defined by every command

    def list(self, key):
        raise NotImplementedError  # To be defined by every command

    @staticmethod
    def now():
        return str(datetime.datetime.now())

    @staticmethod
    def year():
        try:
            return int(BaseTableHandler.execute("SELECT value FROM properties WHERE key = 'year'", fetch='one')[0])
        except TypeError:
            return 481

    def db(self):
        with Database.lock:
            return Database.get()

    @staticmethod
    def execute(sql, param=None, commit=None, fetch=None, many=0):
        """Runs one statement and commits. Database errors are rolled back and re-raised
        (they used to be printed and turned into None, so failed writes looked successful)."""
        with Database.lock:
            conn = Database.get()
            try:
                result = None
                with conn.cursor() as cur:
                    cur.execute(sql, vars=param)
                    if fetch == 'all':
                        result = cur.fetchall()
                    elif fetch == 'one':
                        result = cur.fetchone()
                    elif many:
                        result = cur.fetchmany(many)
                conn.commit()
                return result
            except Exception:
                try:
                    conn.rollback()
                except psycopg2.Error:
                    Database.reset()  # the connection is gone; the next call reconnects
                raise
