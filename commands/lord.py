from commands.base_command import BaseCommand
from database.lordtable import LordTable
from utils import *


class Lord(BaseCommand):

    def __init__(self):
        description = 'Egyes játékosokra vonatkozó beállítások'
        params = ['task']
        super().__init__(description, params, None, longdescription="""
        """)

    async def handle(self, params, message, client):
        me = get_me(message)
        if me:
            i = me.memberid
            if i is None:
                await message.channel.send(f"{me.name}: ehhez a karakterhez nincs játékos rendelve")
                return
            task = params[0].lower()
            if 'setchannel' == task:
                LordTable().set(i, 0, 'mychannel', message.channel.id)
                await message.channel.send(me.name)
            elif task in ('stewardship', 'horses'):
                if len(params) < 2:
                    await message.channel.send(f"Add meg az értéket: {Config.prefix}lord {task} " + ("{szám}" if task == 'stewardship' else "{ló,ló,...}"))
                elif 'stewardship' == task:
                    LordTable().set(i, 0, 'winter.stewardship', params[1])
                    await message.channel.send("Stewardship set")
                else:
                    LordTable().set(i, 0, 'winter.horses', ','.join(params[1:]))
                    await message.channel.send("Horse list set")
            elif 'list' == task:
                # lord table columns: created, modified, year, lord, key, value
                msg = f"```Modified            Lord                 Year Key                  Value\n"
                for row in LordTable().list(lord=i):
                    msg += f"{str(row[0])[:19]:19} {me.name:20} {row[2]:4} {row[4]:20} {row[5]}\n"
                await message.channel.send(msg + "```")
