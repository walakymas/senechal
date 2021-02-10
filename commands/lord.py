from commands.base_command import BaseCommand
from database.lordtable import LordTable
from utils import *


class Lord(BaseCommand):

    def __init__(self):
        description = 'Egyes játékosokra vonatkozó beállítások'
        params = ['task']
        super().__init__(description, params, ['l'], longdescription="""
        """)

    async def handle(self, params, message, client):
        me = get_me(message)
        i = me.memberid
        if me:
            if 'setchannel' == params[0].lower():
                LordTable().set(i, 0, 'mychannel', message.channel.id)
                await message.channel.send(me['name'])
            elif 'stewardship' == params[0].lower():
                LordTable().set(i, 0, 'winter.stewardship', params[0])
                await message.channel.send("Stewardship set")
            elif 'horses' == params[0].lower():
                LordTable().set(i, 0, 'winter.horses', params[0])
                await message.channel.send("Horse list set")
            elif 'list' == params[0].lower():
                rows = LordTable().list()
                msg = f"```Modified                   Lord                 Year Key                  Value\n";
                for row in rows:
                    if i == int(row[2]):
                        msg += f"{row[0]:19} {Character.get_by_memberid(int(row[2])).name:20} {row[1]:4} {row[3]:20} {row[4]}\n"
                await message.channel.send(msg + "```")
