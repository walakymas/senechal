from database.base_table_handler import BaseTableHandler


class LordTable(BaseTableHandler):

    def __init__(self):
        super().__init__('lord')

    def set(self, lord, year, key, value):
        BaseTableHandler.execute('REPLACE INTO lord (modified, lord, year, key, value) VALUES(now(),$1,$2,$3,$4);',
                                 [lord, year, key, value], commit=True)

    def remove(self, lord, year, key):
        BaseTableHandler.execute("DELETE FROM properties WHERE lord=$s, year=$s, key=$s", param=[lord, year, key], commit=True)

    def get(self, lord, year, key):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE lord=$s, year=$s, key = $s", param=[lord, year, key])

    def get_by_value(self, year, key, value):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE year=$s AND key = $s AND value=$s", param=[year, key, value])

    def list(self, lord=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM lord WHERE (-1=%(lord)s::bigint OR lord=%(lord)s::bigint) AND (-1=%(year)s OR year=%(year)s) ORDER BY lord, year, key', {'lord': lord, 'year': year}, fetch='all')

