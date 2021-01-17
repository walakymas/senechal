from database.base_table_handler import BaseTableHandler


class EventsTable(BaseTableHandler):
    # """CREATE TABLE IF NOT EXISTS events (
    #                 id INTEGER PRIMARY KEY,
    #                 modified text,
    #                 created text,
    #                 year int,
    #                 lord int,
    #                 description text,
    #                 glory int
    #                 )
    #                 """
    def __init__(self):
        super().__init__('events')

    def insert(self, lord, description, glory, year=-1):
        return BaseTableHandler.execute('INSERT INTO events (created, modified, year, lord, description, glory) '
                                        'VALUES(now(), now(),$1,$2,$3,$4);',
            [(self.year(), year)[year >= 0], lord, description, glory], commit=True)

    def update(self, id, description, glory):
        return BaseTableHandler.execute('UPDATE events SET modified=now(), description=$1, glory=$2 WHERE id=$3',
                                        [description, glory, id], commit=True)

    def remove(self, id):
        return BaseTableHandler.execute('DELETE * FROM events WHERE id=$1', [id], commit=True)

    def get(self, id):
        return BaseTableHandler.execute('SELECT * FROM events WHERE id=$1', [id], commit=True, fetch='one')

    def list(self, lord=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM events WHERE (-1=$1::bigint OR lord=$1::bigint) '
                                    'AND (-1=$2 OR year=$2) ORDER BY lord, year, id', [lord, year], fetch='all')

    def glory(self, lord=0):
        return BaseTableHandler.execute('SELECT sum(glory) FROM events WHERE lord=$1::bigint', [lord], fetch='one')

