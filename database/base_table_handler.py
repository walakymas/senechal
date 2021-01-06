from database.database import Database
import datetime


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
        return int(BaseTableHandler.execute("SELECT value FROM properties WHERE key = 'year'", fetch='one')[0])

    @staticmethod
    def execute(sql, param=None, commit=None, fetch=None, many=0):
        cur = Database.conn.cursor()
        if param:
            cur.execute(sql, param)
        else:
            cur.execute(sql)
        if commit:
            Database.conn.commit()
        if fetch == 'all':
            return cur.fetchall()
        elif fetch == 'one':
            return cur.fetchone()
        elif many:
            return cur.fetchmany(many)


