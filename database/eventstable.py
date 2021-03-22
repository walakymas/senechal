from database.base_table_handler import BaseTableHandler


class EventsTable(BaseTableHandler):
    def __init__(self):
        super().__init__('events')

    def insert(self, lord, description, glory, year=-1):
        return BaseTableHandler.execute('INSERT INTO events (created, modified, year, lord, description, glory) '
                                        'VALUES(now(), now(),%s,%s,%s,%s);',
            [(self.year(), year)[year > 0], lord, description, glory], commit=True)

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

    def list(self, lord=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM events WHERE (-1=%(lord)s::bigint OR lord=%(lord)s::bigint) '
                                    'AND (-1=%(year)s OR year=%(year)s) ORDER BY lord, year, id', {'lord':lord, 'year':year}, fetch='all')

    def glory(self, lord=0):
        return int(BaseTableHandler.execute('SELECT sum(glory) FROM events WHERE lord=%s::bigint', [lord], fetch='one')[0])

