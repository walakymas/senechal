from commands.base_command import BaseCommand
from utils import *
from config import Config
from database.markstable import MarksTable
from database.lordtable import LordTable
from database.proptable import PropertiesTable


class Db(BaseCommand):

    def __init__(self):
        description = 'Adattáblák kezelése'
        params = ['task']
        super().__init__(description, params,
                         longdescription='''**!db download** adatbázis mentése
**!db [list|set|get|remove] [prop|mark|lord|event|note] ... ** Under construction
prop adatbázis list, set, get és remove művelete valamint a lord és mark adtabázisok list művelete megoldott
        ''')

    async def handle(self, params, message, client):
        msg = None
        if "list" == params[0]:
            msg = ""
            if "prop" == params[1]:
                for row in PropertiesTable().list():
                    msg += f"{str(row[0])[:10]} {row[2]:20} {row[3]}\n"
            elif "lord" == params[1]:
                ch = Config.characters
                for row in LordTable().list():
                    msg += f"{str(row[0])[:10]} {int(row[2]):4} {ch[int(row[3])]['shortName']:10} {row[4]:20} {row[5]}\n"
            elif "mark" == params[1]:
                ch = Config.characters
                for row in MarksTable().list():
                    msg += f"{int(row[4]):3} {str(row[0])[:10]} {row[1]:4} {ch[int(row[2])]['shortName']:10} {row[3]}\n"
            else:
                msg = 'Under Construction'
        elif "set" == params[0]:
            if "prop" == params[1]:
                PropertiesTable().set(params[2], params[3])
                msg = f"Set '{params[2]}' to '{params[3]}'"
            else:
                msg = 'Under Construction'
        elif "get" == params[0]:
            if "prop" == params[1]:
                msg = str(PropertiesTable().get(params[2]))
            else:
                msg = 'Under Construction'
        elif "remove" == params[0]:
            if "prop" == params[1]:
                PropertiesTable().remove(params[2])
                msg = "Removed"
            else:
                msg = 'Under Construction'
        elif "download" == params[0]:
            await try_upload_file(client, message.channel, 'senechal.db', content='Ez itt a mentés')
        else:
            msg = 'Under Construction'
        if msg:
            await message.author.send(msg)
