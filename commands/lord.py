from commands.base_command import BaseCommand
from config import Config
from database import Database
from utils import *


class Lord(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = 0
        params = ['task']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        me = getMe(message)
        if me:
            if 'setchannel' == params[0].lower():
                Database.setLord(message.author.id, 0, 'mychannel', message.channel.id)
                await message.channel.send(me['name'])
            elif 'list' == params[0].lower():
                rows = Database.listLord()
                msg = f"```Modified                   Lord                 Year Key                  Value\n";
                for row in rows:
                    if message.author.id == int(row[2]):
                        msg += f"{row[0]:19} {Config.characters[int(row[2])]['name']:20} {row[1]:4} {row[3]:20} {row[4]}\n"
                await message.channel.send(msg + "```")
