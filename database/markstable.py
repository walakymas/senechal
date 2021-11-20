from database.base_table_handler import BaseTableHandler


class MarksTable(BaseTableHandler):

    def __init__(self):
        super().__init__('marks')

    def set(self, dbid, year, value):
        BaseTableHandler.execute('INSERT INTO marks (modified, dbid, year, spec) VALUES(now(),%(dbid)s,%(year)s,%(spec)s)'
                             ' ON CONFLICT (dbid, year, spec) DO UPDATE SET spec=%(spec)s', {'dbid':dbid, 'year':year, 'spec':value})

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM marks WHERE id=%s", [int(key)])

    def remove_by_name(self, dbid, year, value):
        BaseTableHandler.execute("DELETE FROM marks WHERE dbid=%(dbid)s AND year=%(year)s AND spec=%(spec)s", {'dbid':dbid, 'year':year, 'spec':value})

    def get(self, dbid, year):
        return BaseTableHandler.execute("SELECT * FROM marks WHERE dbid=%s, year=%s", [dbid, year], fetch='all')

    def list(self, dbid=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM marks WHERE (-1=%(dbid)s::bigint OR dbid=%(dbid)s::bigint) AND (-1=%(year)s OR year=%(year)s) ORDER BY dbid, year, spec', {'dbid': dbid, 'year': year}, fetch='all')

