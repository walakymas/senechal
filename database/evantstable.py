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
        BaseTableHandler.execute('INSERT INTO events (created, modified, year, lord, description, glory) VALUES(?,?,?,?,?,?);',
                                 [BaseTableHandler.now(), BaseTableHandler.now(), (self.year(), year)[year >= 0], lord, description, glory], commit=True)

    def update(self, id, description, glory):
        BaseTableHandler.execute('UPDATE events SET modified=?, description=?, glory=? WHERE id=?;',
                                 [BaseTableHandler.now(), description, glory, id], commit=True)

    def remove(self, id):
        BaseTableHandler.execute("DELETE FROM events WHERE id=?", param=[id], commit=True)

    def get(self, id):
        return BaseTableHandler.execute("SELECT * FROM events WHERE id=?", param=[id])

    def list(self, lord=0, year=0):
        return BaseTableHandler.execute('SELECT * FROM events WHERE (0==? OR lord=?) AND (0==? OR year=?) ORDER BY year, lord, id', [lord, lord, year, year], fetch='all')

    def glory(self, lord=0):
        return BaseTableHandler.execute('SELECT sum(glory) FROM events WHERE lord=?', [lord], fetch='one')
