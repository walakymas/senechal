from database.base_table_handler import BaseTableHandler


class LordTable(BaseTableHandler):

    def __init__(self):
        super().__init__('lord')

    def set(self, lord, year, key, value):
        BaseTableHandler.execute('REPLACE INTO lord (modified, lord, year, key, value) VALUES(now(),$1,$2,$3,$4);',
                                 [lord, year, key, value], commit=True)

    def remove(self, lord, year, key):
        BaseTableHandler.execute("DELETE FROM properties WHERE lord=$1, year=$2, key=$3", param=[lord, year, key], commit=True)

    def get(self, lord, year, key):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE lord=$1, year=$2, key = $3", param=[lord, year, key])

    def get_by_value(self, year, key, value):
        return BaseTableHandler.execute("SELECT * FROM lord WHERE year=$1 AND key = $2 AND value=$3", param=[year, key, value])

    def list(self, lord=-1, year=-1):
        return super().db().prepare('SELECT * FROM lord WHERE (-1=$1::bigint OR lord=$1::bigint) AND (-1=$2 OR year=$2) ORDER BY lord, year, key').rows(lord, year)

