import json

from database.base_table_handler import BaseTableHandler


class CharacterTable(BaseTableHandler):

    def __init__(self):
        super().__init__('characters')

    def set_json(self, id, data):
        print(type(data))
        j = json.loads(data)
        BaseTableHandler.execute(
"UPDATE characters SET modified=now(), data=%(data)s, name=%(name)s WHERE id=%(id)s",
                                 {'id': id, 'name': j['name'], 'data': data})

    def get_by_name(self, name):
        return BaseTableHandler.execute(f"SELECT * FROM characters WHERE name ILIKE '%{name}%'", fetch='one')

    def get_by_memberid(self, mid):
        return BaseTableHandler.execute("SELECT * FROM characters WHERE memberid = %s", param=[mid], fetch='one')

    def get_by_id(self, mid):
        return BaseTableHandler.execute("SELECT * FROM characters WHERE id = %s", param=[mid], fetch='one')

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM characters ORDER BY name', fetch='all')

