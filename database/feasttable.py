from database.base_table_handler import BaseTableHandler
import json

class FeastTable(BaseTableHandler):
    def __init__(self):
        super().__init__('feast')

    def get(self, id=-1):
        if id < 0:
            return BaseTableHandler.execute('SELECT * FROM feast ORDER BY cid DESC LIMIT 1', fetch='one')
        else:
            return BaseTableHandler.execute('SELECT * FROM feast WHERE cid=%s', [id], fetch='one')

    def remove(self, id):
        return BaseTableHandler.execute('DELETE FROM feast WHERE id=%s', [id], commit=True)

    def insert(self, feast):
        return BaseTableHandler.execute('INSERT INTO feast (created, modified, title, description, data, deck) '
                                        'VALUES(now(), now(),%s,%s,%s,%s);',
            [feast.title, feast.description, json.dumps(feast.data, ensure_ascii=False), json.dumps({"deck":feast.deck.deck,"pos":feast.deck.pos}, ensure_ascii=False)], commit=True)

    def updateData(self, feast):
        return BaseTableHandler.execute('UPDATE feast SET modified=now(), data = %s WHERE cid=%s',
            [json.dumps(feast.data, ensure_ascii=False), feast.id], commit=True)
    def updateDeck(self, feast):
        return BaseTableHandler.execute('UPDATE feast SET modified=now(), deck = %s WHERE cid=%s',
            [json.dumps(feast.deck.get_data(), ensure_ascii=False), feast.id], commit=True)
    
    def update(self, feast): 
        return BaseTableHandler.execute('UPDATE feast SET modified=now(), title = %s, decription = %s WHERE cid=%s',
            [feast.title, feast.description, feast.id], commit=True)
    # Todo: 

    def list(self): 
        return BaseTableHandler.execute('SELECT * FROM feast ORDER BY cid DESC', fetch='all')

