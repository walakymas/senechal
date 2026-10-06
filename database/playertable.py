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

    def rights(self, did):
        row = BaseTableHandler.execute("SELECT playerrights FROM player WHERE did=%s", param=[did], fetch='one')
        return int(row[0]) if row and row[0] else 0

    def did_by_character(self, character):
        """Discord id of the player who plays the character (None if nobody does)."""
        row = BaseTableHandler.execute("SELECT did FROM player WHERE character=%s", param=[character], fetch='one')
        return int(row[0]) if row and row[0] else None

    def get_by_cid(self, did):
        return BaseTableHandler.execute("SELECT p.* FROM player p WHERE p.character=%s", param=[did], fetch='one')

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM player', fetch='all')
