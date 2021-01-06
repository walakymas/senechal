from commands.base_command import BaseCommand
from utils import *


class Db(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = 0
        params = ['db', 'task']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        msg = None
        if "prop" == params[0]:
            msg = ""
            if "list" == params[1]:
                for row in Database.listProperties():
                    msg += str(row) + "\n"
            elif "set" == params[1]:
                Database.setProperties(params[2], params[3])
                msg = 'Set'
            elif "get" == params[1]:
                Database.getProperties(params[2])
                msg = str(Database.getProperties(params[2]))
            else:
                msg = "Ismeretlen utasítás"
        elif "download" == params[0]:
            ret = await try_upload_file(client, message.channel, 'senechal.db', retries=1, content='Ez itt a mentés')
        else:
            msg = "Ismeretlen utasítás"
        if msg:
            await message.author.send(msg)
