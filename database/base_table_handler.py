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
        try:
            return int(BaseTableHandler.execute("SELECT value FROM properties WHERE key = 'year'", fetch='one')[0])
        except TypeError:
            return 481

    def db(self):
        return Database.db

    @staticmethod
    def execute(sql, param=None, commit=None, fetch=None):
        print(param)
        p = Database.db.query(sql, param)
        if fetch == 'all':
            return p.rows()
        elif fetch == 'one':
            return p.first()
        else:
            p()



