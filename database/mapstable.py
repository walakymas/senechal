from database.base_table_handler import BaseTableHandler

class MapsTable(BaseTableHandler):

    def __init__(self):
        super().__init__('maps')

    def list(self):
        # Return selected columns ordered by ord (display order)
        return BaseTableHandler.execute('SELECT id, created, modified, url, category, ord, name FROM maps ORDER BY ord', fetch='all')

    def get(self, id):
        return BaseTableHandler.execute("SELECT id, created, modified, url, category, ord, name FROM maps WHERE id=%s", param=[id], fetch='one')

    def add(self, url, category, ord, name):
        BaseTableHandler.execute('INSERT INTO maps (created, modified, url, category, ord, name) VALUES(now(), now(), %(url)s, %(category)s, %(ord)s, %(name)s)', {'url': url, 'category': category, 'ord': ord, 'name': name}, commit=True)

    def update(self, id, url, category, ord, name):
        BaseTableHandler.execute('UPDATE maps SET modified=now(), url=%(url)s, category=%(category)s, ord=%(ord)s, name=%(name)s WHERE id=%(id)s', {'id': id, 'url': url, 'category': category, 'ord': ord, 'name': name}, commit=True)

    def remove(self, id):
        BaseTableHandler.execute('DELETE FROM maps WHERE id=%s', param=[id], commit=True)

