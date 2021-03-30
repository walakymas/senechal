import os

from commands.base_command import BaseCommand
from utils import *
import tempfile
import yaml
from database.lordtable import LordTable

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        super().__init__(description, None, ['m', 'en', 'én'],
                         longdescription='''**!me [*|_base_|stats|events|traits|skills|mark|winter|combat] ** információs blokkok a characters.yaml illetve az addatbázisban tárolt eventek alapján
Paraméter nélkül a base blokk jelenik meg, * esetén az összes.
**!me download** a karakterre vonatkozó yaml blokk küldése magán üzenetben 
**!me set stewardship {szám}** a tél fázisra vonatkozó steward dobás
**!me set horses ** a tél fázisba ellenőrzendő lovak listája ,-l elválasztva szóközök nélkül
                         ''')

    async def handle(self, params, message, client):
        (task, *ex) = extract(params, ["base"])
        me = get_me(message)
        if me:
            if "pdf" == task:
                from pdf.sheet import Sheet
                pdf = Sheet(me.get_data(False))
                fp = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names())+"_tmp.pdf")
                pdf.output(fp, 'F')
                await try_upload_file(client, message.author, file_path=fp, filename=str(me.name)+'.pdf', delete_after_send=True)
            else:
                await embed_char(message.channel, me, task, params)
        else:
            print(Config.characters.keys())
