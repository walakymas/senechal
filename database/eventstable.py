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
        return super().db().prepare('INSERT INTO events (created, modified, year, lord, description, glory) VALUES(now(), now(),$1,$2,$3,$4);')((self.year(), year)[year >= 0], lord, description, glory)

    def update(self, id, description, glory):
        return super().db().prepare('UPDATE events SET modified=now(), description=$1, glory=$2 WHERE id=$3')(description, glory, id)

    def remove(self, id):
        return super().db().prepare('DELETE * FROM events WHERE id=$1')(id)

    def get(self, id):
        return super().db().prepare('SELECT * FROM events WHERE id=$1').rows(id)

    def list(self, lord=-1, year=-1):
        return super().db().prepare('SELECT * FROM events WHERE (-1=$1::bigint OR lord=$1::bigint) '
                                    'AND (-1=$2 OR year=$2) ORDER BY lord, year, id').rows(lord, year)

    def glory(self, lord=0):
        return super().db().prepare('SELECT sum(glory) FROM events WHERE lord=$1::bigint').first(lord)
