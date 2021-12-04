from database.base_table_handler import BaseTableHandler


class EventsTable(BaseTableHandler):
    def __init__(self):
        super().__init__('events')

    def insert(self, dbid, description, glory, year=-1):
        return BaseTableHandler.execute('INSERT INTO events (created, modified, year, dbid, description, glory) '
                                        'VALUES(now(), now(),%s,%s,%s,%s);',
            [(self.year(), year)[year > 0], dbid, description, glory], commit=True)

    def update(self, id, description, glory, year):
        return BaseTableHandler.execute('UPDATE events SET modified=now(), description=%s, glory=%s, year=%s WHERE id=%s',
                                        [description, glory, year, id], commit=True)


    def update_wo_year(self, id, description, glory):
        return BaseTableHandler.execute('UPDATE events SET modified=now(), description=%s, glory=%s WHERE id=%s',
                                        [description, glory, id], commit=True)

    def remove(self, id):
        return BaseTableHandler.execute('DELETE FROM events WHERE id=%s', [id], commit=True)

    def get(self, id):
        return BaseTableHandler.execute('SELECT * FROM events WHERE id=%s', [id], commit=True, fetch='one')

    def list(self, dbid=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM events WHERE (-1=%(dbid)s::bigint OR dbid=%(dbid)s::bigint) '
                                    'AND (-1=%(year)s OR year=%(year)s) ORDER BY dbid, year, id', {'dbid':dbid, 'year':year}, fetch='all')

    def glory(self, dbid=0):
        try:
            return int(BaseTableHandler.execute('SELECT sum(glory) FROM events WHERE dbid=%s::bigint', [dbid], fetch='one')[0])
        except TypeError:
            return 0

