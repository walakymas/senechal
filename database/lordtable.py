from database.base_table_handler import BaseTableHandler


class LordTable(BaseTableHandler):

    def __init__(self):
        super().__init__('lord')

    def set(self, lord, year, key, value):
        BaseTableHandler.execute('REPLACE INTO lord (last_modified, lord, year, key, value) VALUES(?,?,?,?,?);',
                                 [BaseTableHandler.now(), lord, year, key, value])

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM properties WHERE key=?", param=[key])

    def get(self, lord, year, key):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE lord=?, year=?, key = ?", param=[lord, year, key])

    def getbyvalue(self, year, key, value):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE year=?, key = ?, value=?", param=[year, key, value])

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM lord ORDER BY lord, key', fetch='all')

