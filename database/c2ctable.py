import logging
from database.base_table_handler import BaseTableHandler

log = logging.getLogger(__name__)


class C2CTable(BaseTableHandler):

    def __init__(self):
        super().__init__('c2c')

    def add(self, c0, c1, connection, comment):
        BaseTableHandler.execute('INSERT INTO c2c (modified, c0, c1, connection, comment) VALUES(now(),'
                                 ' %(c0)s, %(c1)s, %(connection)s, %(comment)s)'
                                 ' ON CONFLICT (c0, c1) DO UPDATE SET connection=%(connection)s, comment=%(comment)s',
                                 {'c0': c0, 'c1': c1, 'connection': connection, 'comment': comment}) 
  
    def remove(self, c0, c1):
        BaseTableHandler.execute("DELETE FROM c2c WHERE c0=%(c0)s and c1=%(c1)s", param={'c0': c0, 'c1': c1}, commit=True)

    def get(self, c0,  c1):
        return BaseTableHandler.execute("SELECT * FROM c2c WHERE c0=%(c0)s and c1=%(c1)s", param={'c0': c0, 'c1': c1}, fetch='one')

    def list(self, c=-1):
        return BaseTableHandler.execute('SELECT * FROM c2c '
                                        ' WHERE -1=%(c)s OR c0=%(c)s::bigint OR c1=%(c)s::bigint '
                                        ' ORDER BY c0, c1', {'c': c}, fetch='all')

