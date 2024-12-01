from database.base_table_handler import BaseTableHandler


class PlayerTable(BaseTableHandler):

    def __init__(self):
        super().__init__('player')

    def set(self, lord, year, key, value):
        BaseTableHandler.execute('INSERT INTO player (modified, lord, year, key, value) VALUES(now(),'
                                 ' %(lord)s, %(year)s, %(key)s, %(value)s)'
                                 ' ON CONFLICT (lord, year, key) DO UPDATE SET value=%(value)s',
                                 {'lord': lord, 'year': year, 'key': key, 'value': value})

    def remove(self, id):
        BaseTableHandler.execute("DELETE FROM properties WHERE id=%s", param=[id], commit=True)

    def get(self, id):
        return BaseTableHandler.execute("SELECT * FROM player WHERE cid=%s", param=[id], fetch='one')

    def get_by_did(self, did):
        return BaseTableHandler.execute("SELECT * FROM player WHERE did=%s", param=[did], fetch='one')

    def get_by_cid(self, did):
        return BaseTableHandler.execute("SELECT p.* FROM player p JOIN characters c ON c.memberid=p.did WHERE c.id=%s", param=[did], fetch='one')

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM player', fetch='all')

