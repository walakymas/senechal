from database.base_table_handler import BaseTableHandler


class MarksTable(BaseTableHandler):
    # Result of the winter check of a mark (marks.status). A new mark is UNCHECKED; the winter rolls the UNCHECKED ones
    # (FAILED / INCREASE), the update raises the value of the INCREASE ones and makes them UPDATED.
    UNCHECKED = 'Unchecked'
    FAILED = 'Failed'
    INCREASE = 'Increase'
    UPDATED = 'Updated'
    STATUSES = (UNCHECKED, FAILED, INCREASE, UPDATED)
    # marks table columns: id 0, created 1, modified 2, year 3, lord 4 (obsolete), spec 5, dbid 6, status 7

    def __init__(self):
        super().__init__('marks')

    def set(self, dbid, year, value):
        BaseTableHandler.execute('INSERT INTO marks (modified, dbid, year, spec) VALUES(now(),%(dbid)s,%(year)s,%(spec)s)'
                             ' ON CONFLICT (dbid, year, spec) DO UPDATE SET spec=%(spec)s', {'dbid':dbid, 'year':year, 'spec':value})

    def set_status(self, key, status):
        self.set_status_many([key], status)

    def set_status_many(self, keys, status):
        if status not in MarksTable.STATUSES:
            raise ValueError(f"Unknown mark status: {status}")
        BaseTableHandler.execute("UPDATE marks SET status=%s, modified=now() WHERE id = ANY(%s)",
                                 [status, [int(k) for k in keys]])

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM marks WHERE id=%s", [int(key)])

    def remove_by_name(self, dbid, year, value):
        BaseTableHandler.execute("DELETE FROM marks WHERE dbid=%(dbid)s AND year=%(year)s AND spec=%(spec)s", {'dbid':dbid, 'year':year, 'spec':value})

    def get(self, dbid, year):
        return BaseTableHandler.execute("SELECT * FROM marks WHERE dbid=%s AND year=%s", [dbid, year], fetch='all')

    def list_for(self, dbids, year):
        """{dbid: [spec, ...]} of the marks of several characters in one year (one query)."""
        rows = BaseTableHandler.execute('SELECT * FROM marks WHERE dbid = ANY(%s) AND year = %s ORDER BY dbid, year, spec',
                                        [list(dbids), year], fetch='all')
        marks = {}
        for row in rows:
            marks.setdefault(row[6], []).append(row[5])
        return marks

    def list(self, dbid=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM marks WHERE (-1=%(dbid)s::bigint OR dbid=%(dbid)s::bigint) AND (-1=%(year)s OR year=%(year)s) ORDER BY dbid, year, spec', {'dbid': dbid, 'year': year}, fetch='all')

