from database.base_table_handler import BaseTableHandler


class P2CTable(BaseTableHandler):

    def __init__(self):
        super().__init__('p2c')

    def add(self, player, character, connection, comment):
        BaseTableHandler.execute('INSERT INTO p2c (modified, player, character, connection, comment) VALUES(now(),'
                                 ' %(player)d, %(character)d, %(connection)s, %(comment)s)'
                                 ' ON CONFLICT (player, character) DO UPDATE SET connection=%(connection)s, comment=%(comment)s',
                                 {'player': player, 'character': character, 'connection': connection, 'comment': comment})
  
    def remove(self, player, character):
        BaseTableHandler.execute("DELETE FROM p2c WHERE player=%s, character=%s", param=[player, character], commit=True)

    def get(self, player, character):
        return BaseTableHandler.execute("SELECT * FROM p2c WHERE player=%s, character=%s", param=[player, character])

    def list(self, player=-1, character=-1):
        return BaseTableHandler.execute('SELECT * FROM p2c '
                                        ' WHERE (-1=%(player)s::bigint OR player=%(player)s::bigint) '
                                        '   AND (-1=%(character)s::bigint OR character=%(character)s::bigint) '
                                        ' ORDER BY player, character', {'player': player, 'character': character}, fetch='all')

