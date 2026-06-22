from database.base_table_handler import BaseTableHandler

class MapsTable(BaseTableHandler):

    def __init__(self):
        super().__init__('maps')

    def list(self):
        # Return all maps ordered by ord (display order)
        return BaseTableHandler.execute('SELECT * FROM maps ORDER BY ord', fetch='all')

    def get(self, id):
        return BaseTableHandler.execute("SELECT * FROM maps WHERE id=%s", param=[id], fetch='one')