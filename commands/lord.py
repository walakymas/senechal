from commands.base_command import BaseCommand
from database.lordtable import LordTable
from utils import *


class Lord(BaseCommand):

    def __init__(self):
        description = 'Egyes játékosokra vonatkozó beállítások, egyelőre csak a saját channel rögzítésére'
        params = ['task']
        super().__init__(description, params, ['l'])

    async def handle(self, params, message, client):
        me = get_me(message)
        i = me['memberId']
        if me:
            if 'setchannel' == params[0].lower():
                LordTable().set(i, 0, 'mychannel', message.channel.id)
                await message.channel.send(me['name'])
            elif 'list' == params[0].lower():
                rows = LordTable().list()
                msg = f"```Modified                   Lord                 Year Key                  Value\n";
                for row in rows:
                    if i == int(row[2]):
                        msg += f"{row[0]:19} {Config.characters[int(row[2])]['name']:20} {row[1]:4} {row[3]:20} {row[4]}\n"
                await message.channel.send(msg + "```")
