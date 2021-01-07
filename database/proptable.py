from database.base_table_handler import BaseTableHandler


class PropertiesTable(BaseTableHandler):

    def __init__(self):
        super().__init__('properties')

    def set(self, key, value):
        BaseTableHandler.execute('REPLACE INTO properties (last_modified, key, value) VALUES(?,?,?);',
                                 [BaseTableHandler.now(), key, value], commit=True)

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM properties WHERE key=?", param=[key], commit=True)

    def get(self, key):
        return BaseTableHandler.execute("SELECT * FROM properties WHERE key=?", param=[key])

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM properties ORDER BY key', fetch='all')

