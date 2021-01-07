from database.base_table_handler import BaseTableHandler


class MarksTable(BaseTableHandler):

    def __init__(self):
        super().__init__('marks')

    def set(self, lord, year, value):
        BaseTableHandler.execute('REPLACE INTO marks (last_modified, lord, year, spec) VALUES(?,?,?,?);',
                                 [BaseTableHandler.now(), lord, year, value], commit=True)

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM marks WHERE id=?", param=[key], commit=True)

    def get(self, lord, year):
        return BaseTableHandler.execute("SELECT * FROM marks WHERE lord=?, year=?", param=[lord, year])

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM marks ORDER BY lord, year, spec', fetch='all')

