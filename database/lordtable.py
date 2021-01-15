from database.base_table_handler import BaseTableHandler


class LordTable(BaseTableHandler):

    def __init__(self):
        super().__init__('lord')

    def set(self, lord, year, key, value):
        BaseTableHandler.execute('REPLACE INTO lord (last_modified, lord, year, key, value) VALUES(?,?,?,?,?);',
                                 [BaseTableHandler.now(), lord, year, key, value], commit=True)

    def remove(self, lord, year, key):
        BaseTableHandler.execute("DELETE FROM properties WHERE lord=?, yar=key, key=?", param=[key], commit=True)

    def get(self, lord, year, key):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE lord=?, year=?, key = ?", param=[lord, year, key])

    def get_by_value(self, year, key, value):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE year=? AND key = ? AND value=?", param=[year, key, value])

    def list(self, lord=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM lord WHERE (?==-1 OR lord=?) AND (?==-1 OR year=?) ORDER BY '
                                        'lord, year, key',  [lord, lord, year, year], fetch='all')

