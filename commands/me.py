import os

from disputils import EmbedPaginator

from commands.base_command import BaseCommand
from utils import *
import tempfile
import yaml
from database.lordtable import LordTable

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        super().__init__(description, None, ['m', 'en', 'én'],
                         longdescription='''**!me [*|_base_|events|traits|passions|skills|mark|winter|combat] ** információs blokkok a characters.yaml illetve az addatbázisban tárolt eventek alapján
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
            elif "page" == task:
                embeds = [
                    Embed(
                        title="test page 1",
                        description="This is just some tests content!",
                        color=0x115599,
                    ),
                    Embed(
                        title="test page 2",
                        description="Nothing interesting here.",
                        color=0x5599FF,
                    ),
                    Embed(
                        title="test page 3",
                        description="Why are you still here?",
                        color=0x191638,
                    ),
                ]

                paginator = EmbedPaginator(client, embeds)
                await paginator.run([message.author], channel=message.channel)
            else:
                await embed_char(message.channel, me, task, params, client, message)
        else:
            print(Config.characters.keys())
