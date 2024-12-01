from database.base_table_handler import BaseTableHandler


class TokenTable(BaseTableHandler):

    def __init__(self):
        super().__init__('tokens')

    def set(self, token, cid, expires, tokenstate):
        print(f"{token} {cid} {expires} {tokenstate}")
        BaseTableHandler.execute('INSERT INTO tokens (modified, token, cid, expires) VALUES(now(),%(token)s,%(cid)s, now())'
                                 ' ON CONFLICT (token) DO UPDATE SET modified=now(), tokenstate=%(tokenstate)s', 
                                 {'token': token, 'cid': cid, 'tokenstate':tokenstate, 'expires':expires})

    def enable(self, token):
        BaseTableHandler.execute("UPDATE tokens SET tokenstate=1, expires = now() + INTERVAL '1 DAYS' WHERE token=%s", param=[token], commit=True)

    def remove(self, token):
        BaseTableHandler.execute("DELETE FROM tokens set  WHERE key=%s", param=[token], commit=True)

    def get(self, id):
        return BaseTableHandler.execute("SELECT * FROM tokens t LEFT JOIN player p ON p.id = t.cid WHERE token=%s", param=[token], fetch='one')

    def get_info_by_id(self, id):
        return BaseTableHandler.execute("SELECT token, p.did, expires, tokenstate FROM tokens t LEFT JOIN player p ON p.cid = t.cid WHERE t.id = %s", param=[id], fetch='one')

    def get_info_by_token(self, token):
        return BaseTableHandler.execute("SELECT id, p.did, expires, tokenstate FROM tokens t LEFT JOIN player p ON p.cid = t.cid WHERE t.token = %s", param=[token], fetch='one')

    def list(self):
        return BaseTableHandler.execute('SELECT * FROM tokens ORDER BY id desc', fetch='all')

