from commands.base_command import BaseCommand
from utils import *
import tempfile
import yaml
from database.lordtable import LordTable

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        super().__init__(description, None, ['m', 'en', 'én'],
                         longdescription='''**!me [*|_base_|stats|events|traits|skills] ** információs blokkok a characters.yaml illetve az addatbázisban tárolt eventek alapján
Paraméter nélkül a base blokk jelenik meg, * esetén az összes.
**!me download** a karakterre vonatkozó yaml blokk küldése magán üzenetben 
**!me set stewardship {szám}** a tél fázisra vonatkozó steward dobás
**!me set horses ** a tél fázisba ellenőrzendő lovak listája ,-l elválasztva szóközök nélkül
                         ''')

    async def handle(self, params, message, client):
        (task,*ex) = extract(params, ["base"])
        me = get_me(message)
        if me:
            i = me['memberId']
            if "download" == task:
                me2 = Config.charactersOrig[i]
                fp = next(tempfile._get_candidate_names())
                with open(fp, 'w') as file:
                    yaml.dump(me2, file, allow_unicode=True)
                await try_upload_file(client, message.author, file_path=fp, filename=str(me['name'])+'.yaml', delete_after_send=True)
            elif "pdf" == task:
                from pdf.sheet import Sheet
                pdf = Sheet(me)
                pdf.fill()
                fp = next(tempfile._get_candidate_names())
                pdf.output(fp, 'F')
                await try_upload_file(client, message.author, file_path=fp, filename=str(me['name'])+'.pdf', delete_after_send=True)
            elif "set" == task:
                if len(params) < 3:
                    await message.channel.send("!me send [stewardship,horses] {value}")
                elif params[1] == 'stewardship':
                    LordTable().set(i, 0, 'winter.stewardship', params[2])
                    await message.channel.send("updated")
                elif params[1] == 'horses':
                    LordTable().set(i, 0, 'winter.horses', params[2])
                    await message.channel.send("updated")
                else:
                    await message.channel.send("!me send [senechal,horses] {value}")
            else:
                await embed_pc(message.channel, me, task, params)
        else:
            print(Config.characters.keys())
