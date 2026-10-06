import asyncio
import os

from commands.base_command import BaseCommand
from utils import *
import tempfile
import yaml
from database.lordtable import LordTable
from database.playertable import PlayerTable
from database.proptable import PropertiesTable

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        super().__init__(description, None, ['m', 'en', 'én'],
                         longdescription='''**!me [*|_base_|events|traits|passions|skills|mark|winter|combat] ** információs blokkok a characters.yaml illetve az addatbázisban tárolt eventek alapján
Paraméter nélkül a base blokk jelenik meg, * esetén az összes.
**!me download** a karakterre vonatkozó yaml blokk küldése magán üzenetben 
**!me setChannel** az aktuális channel beállítása a neked szánt üzenetek helyéül
**!me set stewardship {szám}** a tél fázisra vonatkozó steward dobás
**!me set horses ** a tél fázisba ellenőrzendő lovak listája ,-l elválasztva szóközök nélkül
                         ''')

    async def handle(self, params, message, client):
        (task, *ex) = extract(params, ["base"])
        me = get_me(message)
        if "setchannel" == task.lower():
            player = PlayerTable().get_by_did(message.author.id)
            if player:
                PropertiesTable().set(f"{Config.prefix}channel{player[0]}", str(message.channel.id))
                await message.channel.send(f"Channel set: {message.channel.id}")
            else:
                await message.channel.send(message.author.mention + " Téged nem ismerlek sajnos")
        elif me:
            if "pdf" == task:
                from pdf.sheet import Sheet
                pdf = Sheet(me)
                fp = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names())+"_tmp.pdf")
                await asyncio.to_thread(pdf.output, fp)
                await try_upload_file(client, message.author, file_path=fp, filename=str(me.name)+'.pdf', delete_after_send=True)
            else:
                await embed_char(message.channel, me, task, params, client, message)
        else:
            await message.channel.send(message.author.mention + " Téged nem ismerlek sajnos")
