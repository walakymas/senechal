import os

from commands.base_command import BaseCommand
from utils import *
from config import Config
from database.markstable import MarksTable
from database.lordtable import LordTable
from database.proptable import PropertiesTable
from permissions import has_rights, NO_RIGHTS


# Number of parameters (including the task) each task needs
NEEDED = {'list': 2, 'get': 3, 'remove': 3, 'set': 4}


def short_name(character, fallback):
    return str(fallback) if character is None else character.data.get('shortName', character.name)


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
        # Everything needs admin rights except a player setting their own lord data (`!db set lord`)
        own_lord = len(params) > 1 and params[0] == "set" and params[1] == "lord"
        if not own_lord and not has_rights(message.author.id):
            await message.channel.send(message.author.mention + NO_RIGHTS)
            return
        if params[0] in NEEDED and len(params) < NEEDED[params[0]]:
            await message.author.send(f"Hiányzó paraméter: {Config.prefix}db {params[0]} legalább {NEEDED[params[0]]} paramétert vár")
            return
        msg = None
        if "list" == params[0]:
            msg = ""
            if "prop" == params[1]:
                for row in PropertiesTable().list():
                    msg += f"{str(row[0])[:10]} {row[2]:20} {row[3]}\n"
            elif "lord" == params[1]:
                for row in LordTable().list():
                    msg += f"{str(row[0])[:10]} {int(row[2]):4} {short_name(Character.get_by_memberid(row[3]), row[3]):10} {row[4]:20} {row[5]}\n"
            elif "mark" == params[1]:
                for row in MarksTable().list():
                    msg += f"{int(row[0]):3} {str(row[1])[:10]} {row[3]:4} {short_name(Character.get_by_id(row[6]), row[6]):10} {row[5]}\n"
            else:
                msg = 'Under Construction'
        elif "set" == params[0]:
            if "prop" == params[1]:
                PropertiesTable().set(params[2], params[3])
                msg = f"Set '{params[2]}' to '{params[3]}'"
            elif "lord" == params[1]:
                me = get_me(message)
                if me:
                    LordTable().set(me.memberid, 0, params[2], params[3])
                    msg = f"Set '{params[2]}' to '{params[3]}'"
                else:
                    msg = f"Őnt nem ismerem sajnos"
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
            if os.path.isfile('senechal.db'):
                await try_upload_file(client, message.channel, 'senechal.db', content='Ez itt a mentés')
            else:
                msg = 'Nincs mentés: az adatbázis PostgreSQL, a mentéshez használd a pg_dump-ot'
        else:
            msg = 'Under Construction'
        if msg:
            await message.author.send(msg)
