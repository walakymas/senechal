from database.base_table_handler import BaseTableHandler


class MarksTable(BaseTableHandler):

    def __init__(self):
        super().__init__('marks')

    def set(self, lord, year, value):
        BaseTableHandler.execute('INSERT INTO marks (modified, lord, year, spec) VALUES(now(),%(lord)s,%(year)s,%(spec)s)'
                             ' ON CONFLICT (lord, year, spec) DO UPDATE SET spec=%(spec)s', {'lord':lord, 'year':year, 'spec':value})

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM marks WHERE id=%s", [int(key)])

    def remove_by_name(self, lord, year, value):
        BaseTableHandler.execute("DELETE FROM marks WHERE lord=%(lord)s AND year=%(year)s AND spec=%(spec)s", {'lord':lord, 'year':year, 'spec':value})

    def get(self, lord, year):
        return BaseTableHandler.execute("SELECT * FROM marks WHERE lord=%s, year=%s", [lord, year], fetch='all')

    def list(self, lord=-1, year=-1):
        return BaseTableHandler.execute('SELECT * FROM marks WHERE (-1=%(lord)s::bigint OR lord=%(lord)s::bigint) AND (-1=%(year)s OR year=%(year)s) ORDER BY lord, year, spec', {'lord': lord, 'year': year}, fetch='all')

