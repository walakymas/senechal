from database.base_table_handler import BaseTableHandler


class P2PTable(BaseTableHandler):

    def __init__(self):
        super().__init__('p2p')

    def add(self, player0, player1, connection, comment):
        if player0 > player1:
            p = player1
            player1 = player0
            player0 = p 
        BaseTableHandler.execute('INSERT INTO p2p (modified, player0, player1, connection, comment) VALUES(now(),'
                                 ' %(player0)d, %(player1)d, %(connection)s, %(comment)s)'
                                 ' ON CONFLICT (player0, player1) DO UPDATE SET connection=%(connection)s, comment=%(comment)s',
                                 {'player0': player0, 'player1': player1, 'connection': connection, 'comment': comment})
  
    def remove(self, player0, player1):
        if player0 > player1:
            p = player1
            player1 = player0
            player0 = p 
        BaseTableHandler.execute("DELETE FROM p2c WHERE playe0r=%s, player1=%s", param=[player0, player1], commit=True)

    def get(self, player0,  player1):
        if player0 > player1:
            p = player1
            player1 = player0
            player0 = p 
        return BaseTableHandler.execute("SELECT * FROM p2c WHERE player0=%s, player1=%s", param=[player0, player1])

    def list(self, player):
        return BaseTableHandler.execute('SELECT * FROM p2c '
                                        ' WHERE player0=%(player)s::bigint OR player=%(player)s::bigint '
                                        ' ORDER BY player, character', {'player': player}, fetch='all')

