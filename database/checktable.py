from database.base_table_handler import BaseTableHandler


class CheckTable(BaseTableHandler):

    def __init__(self):
        super().__init__('check')

    def add(self, character, command, result):

        BaseTableHandler.execute('INSERT INTO checks (character, command, result) VALUES('
                                 ' %(character)s, %(command)s, %(result)s)',
                                 {'character':character, 'command':command, 'result':result})
  
    def remove(self, cid):
        BaseTableHandler.execute("DELETE FROM checks WHERE cid=%s", param=[cid], commit=True)

    def list(self, plyr=None, limit=5 ):
        return BaseTableHandler.execute('SELECT *, (select name FROM characters chr WHERE chr.id = c.character) name '
            ' FROM checks c WHERE %(plyr)s IS null '
            ' OR character IN (SELECT id from characters where player = %(plyr)s)'
            ' ORDER BY created DESC LIMIT %(limit)s', 
            {'limit': limit, 'plyr':plyr}, fetch='all')

