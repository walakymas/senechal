from database.base_table_handler import BaseTableHandler


class C2CTable(BaseTableHandler):

    def __init__(self):
        super().__init__('c2c')

    def add(self, c0, c1, connection, comment):
        if c0 > c1:
            p = c1
            c1 = c0
            c0 = p 
        BaseTableHandler.execute('INSERT INTO c2c (modified, c0, c1, connection, comment) VALUES(now(),'
                                 ' %(c0)d, %(c1)d, %(connection)s, %(comment)s)'
                                 ' ON CONFLICT (c0, c1) DO UPDATE SET connection=%(connection)s, comment=%(comment)s',
                                 {'c0': c0, 'c1': c1, 'connection': connection, 'comment': comment})
  
    def remove(self, c0, c1):
        if c0 > c1:
            p = c1
            c1 = c0
            c0 = p 
        BaseTableHandler.execute("DELETE FROM c2c WHERE playe0r=%s, c1=%s", param=[c0, c1], commit=True)

    def get(self, c0,  c1):
        if c0 > c1:
            p = c1
            c1 = c0
            c0 = p 
        return BaseTableHandler.execute("SELECT * FROM c2c WHERE c0=%s, c1=%s", param=[c0, c1])

    def list(self, c):
        return BaseTableHandler.execute('SELECT * FROM c2c '
                                        ' WHERE c0=%(c)s::bigint OR c=%(c)s::bigint '
                                        ' ORDER BY c0, c1', {'c': c}, fetch='all')

