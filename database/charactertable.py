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
        if 'role' in j:
            role = j['role']
        if 'player' in j:
            player = j['player']
        BaseTableHandler.execute("UPDATE characters SET modified=now(), data=%(data)s, name=%(name)s, url=%(url)s, role=%(role)s  WHERE id=%(id)s",
                                 {'id': id, 'name': j['name'], 'data': data, 'url': url, 'role': role})
        if player is not None and str(player).strip() != '':
            BaseTableHandler.execute("UPDATE characters SET player=%(player)s WHERE id=%(id)s",
                                     {'id': id, 'player': int(player)})

    @staticmethod
    def like_pattern(text):
        """Substring pattern for ILIKE; \\, % and _ in the text match literally."""
        escaped = str(text).replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        return f"%{escaped}%"

    # The records below are `characters.*` plus the Discord id of the player (`p.did`, index 9), so that a Character
    # needs no query of its own to find its player.
    def get_by_name(self, name):
        return BaseTableHandler.execute("SELECT c.*, p.did FROM characters c LEFT JOIN player p ON p.character = c.id "
                                        "WHERE c.name ILIKE %s ORDER BY c.id, p.cid",
                                        param=[CharacterTable.like_pattern(name)], fetch='one')

    def get_by_memberid(self, mid):
        return BaseTableHandler.execute("SELECT c.*, p.did FROM characters c join player p on p.character = c.id WHERE p.did = %s", param=[mid], fetch='one')

    def get_by_id(self, mid):
        return BaseTableHandler.execute("SELECT c.*, p.did FROM characters c LEFT JOIN player p ON p.character = c.id "
                                        "WHERE c.id = %s ORDER BY p.cid", param=[mid], fetch='one')

    def get_by_ids(self, ids):
        """One record per character id (the first player's did if there are several)."""
        rows = BaseTableHandler.execute("SELECT c.*, p.did FROM characters c LEFT JOIN player p ON p.character = c.id "
                                        "WHERE c.id = ANY(%s) ORDER BY c.id, p.cid", param=[list(ids)], fetch='all')
        records = {}
        for row in rows:
            records.setdefault(row[0], row)
        return records

    def get_pcs(self):
        return BaseTableHandler.execute("SELECT c.*, p.did FROM characters c JOIN player p ON p.character = c.id", fetch='all')

    def list(self):
        return BaseTableHandler.execute('SELECT c.*, p.did as pmid FROM characters c LEFT JOIN player p ON p.character = c.id ORDER BY name', fetch='all')

    def list_summary(self):
        """What the character lists need (no `data` JSON): id, modified, name, url, role, player, pmid."""
        return BaseTableHandler.execute('SELECT c.id, c.modified, c.name, c.url, c.role, c.player, p.did as pmid '
                                        'FROM characters c LEFT JOIN player p ON p.character = c.id ORDER BY c.name', fetch='all')

