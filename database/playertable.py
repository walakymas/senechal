from database.base_table_handler import BaseTableHandler

# TODO
class PlayerTable(BaseTableHandler):

    def __init__(self):
        super().__init__('player')

    def set(self, name):
        BaseTableHandler.execute('INSERT INTO player (modified, name) VALUES(now(),  %(name)s)', {'name': name})

    def remove(self, lord, year, key):
        BaseTableHandler.execute("DELETE FROM player WHERE lord=%s, year=%s, key=%s", param=[lord, year, key], commit=True)

    def get(self, lord, year, key):
        return BaseTableHandler.execute("SELECT * FROM player WHERE lord=%s, year=%s, key = %s", param=[lord, year, key])

    def get_by_value(self, year, key, value):
        return BaseTableHandler.execute("SELECT * FROM player WHERE year=%s AND key = %s AND value=%s", param=[year, key, value])

    def list(self, lord=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM player WHERE (-1=%(lord)s::bigint OR lord=%(lord)s::bigint) AND (-1=%(year)s OR year=%(year)s) ORDER BY lord, year, key', {'lord': lord, 'year': year}, fetch='all')

