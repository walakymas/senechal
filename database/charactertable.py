import json

from database.base_table_handler import BaseTableHandler


class CharacterTable(BaseTableHandler):

    def __init__(self):
        super().__init__('characters')

    def add(self, data):
        j = json.loads(data)
        BaseTableHandler.execute(
            "INSERT INTO characters (created, modified, data, name) VALUES (now(), now(), %(data)s, %(name)s)",
            {'name': j['name'], 'data': data}, commit=True)

    def set_json(self, id, data):
        j = json.loads(data)
        url = None
        memberid = None
        role = None
        player = None
        j['dbid'] = id
        if 'url' in j:
            url = j['url']
        if 'memberId' in j:
            memberid = j['memberId']
        if 'role' in j:
            role = j['role']
        if 'player' in j:
            player = j['player']
        BaseTableHandler.execute("UPDATE characters SET modified=now(), data=%(data)s, name=%(name)s, url=%(url)s, memberid=%(memberid)s , role=%(role)s , player=%(player)s  WHERE id=%(id)s",
                                 {'id': id, 'name': j['name'], 'data': data, 'url': url, 'memberid': memberid, 'role': role, 'player': player})

    def get_by_name(self, name):
        return BaseTableHandler.execute(f"SELECT * FROM characters WHERE name ILIKE '%{name}%'", fetch='one')

    def get_by_memberid(self, mid):
        return BaseTableHandler.execute("SELECT * FROM characters WHERE memberid = %s", param=[mid], fetch='one')

    def get_by_id(self, mid):
        return BaseTableHandler.execute("SELECT * FROM characters WHERE id = %s", param=[mid], fetch='one')

    def get_pcs(self):
        return BaseTableHandler.execute("SELECT c.* FROM characters c JOIN player p ON p.character = c.id", fetch='all')

    def list(self):
        return BaseTableHandler.execute('SELECT c.*, p.did as pmid FROM characters c LEFT JOIN player p ON p.character = c.id ORDER BY name', fetch='all')

