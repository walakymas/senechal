from database.base_table_handler import BaseTableHandler

# TODO
class PlayerTable(BaseTableHandler):

    def __init__(self):
        super().__init__('player')

    def set(self, name):
        BaseTableHandler.execute('INSERT INTO player (modified, name) VALUES(now(),  %(name)s)', {'name': name})

    def remove(self, id):
        BaseTableHandler.execute("DELETE FROM properties WHERE id=%s", param=[id], commit=True)

    def get(self, id):
        r = BaseTableHandler.execute("SELECT * FROM player WHERE cid=%s", param=[id], fetch='one')
        print(f"player get:{r}")
        return r

    def get_by_did(self, did):
        return BaseTableHandler.execute("SELECT * FROM player WHERE did=%s", param=[did], fetch='one')

    def get_by_cid(self, did):
        return BaseTableHandler.execute("SELECT p.* FROM player p JOIN characters c ON c.memberid=p.did WHERE c.id=%s", param=[did], fetch='one')

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM player', fetch='all')
