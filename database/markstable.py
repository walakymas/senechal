from database.base_table_handler import BaseTableHandler


class MarksTable(BaseTableHandler):

    def __init__(self):
        super().__init__('marks')

    def set(self, lord, year, value):
        super().db().prepare('INSERT INTO marks (modified, lord, year, spec) VALUES(now(),$1,$2,$3)'
                             ' ON CONFLICT (lord, year, spec) DO UPDATE SET spec=$3')(lord, year, value)

    def remove(self, key):
        super().db().prepare("DELETE FROM marks WHERE id=$1")(int(key))

    def get(self, lord, year):
        return super().db().prepare("SELECT * FROM marks WHERE lord=$1, year=$2")(lord, year)

    def list(self, lord=-1, year=-1):
        return super().db().prepare('SELECT * FROM marks WHERE (-1=$1::bigint OR lord=$1::bigint) AND (-1=$2 OR year=$2) ORDER BY lord, year, spec').rows(lord, year)

