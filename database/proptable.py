from database.base_table_handler import BaseTableHandler


class PropertiesTable(BaseTableHandler):

    def __init__(self):
        super().__init__('properties')

    def set(self, key, value):
        BaseTableHandler.execute('INSERT INTO properties (modified, key, value) VALUES(now(),%(key)s,%(value)s)'
                                 ' ON CONFLICT (key) DO UPDATE SET value=%(value)s', {'key':key, 'value':value})

    def remove(self, key):
        BaseTableHandler.execute("DELETE FROM properties WHERE key=%s", param=[key], commit=True)

    def get(self, key):
        return BaseTableHandler.execute("SELECT * FROM properties WHERE key=%s", param=[key])

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM properties ORDER BY key', fetch='all')

