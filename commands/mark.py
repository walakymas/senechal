from commands.base_command import BaseCommand
from database import Database
from utils import *


class Mark(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = 0
        params = ['spec']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        me = getMe(message)
        year = int(Database.getProperties('year')[2])
        if me:
            if 'list' == params[0].lower():
                rows = Database.listMark()
                msg = f"```{me['name']} Év:{year} \nID  Modified            Lord                 Year Spec\n";
                marks = []
                for row in rows:
                    if message.author.id == int(row[2]) and year == int(row[1]):
                        if row[3] not in marks:
                            marks.append(row[3])
                            msg += f"{row[4]:3} {row[0][:10]} {row[3]:15}\n"
                await message.channel.send(msg + "```")
            elif 'remove' == params[0].lower():
                Database.delMark(params[1])
                await message.channel.send("removed")
            else:
                msg = f"Year:{year}\n"
                for t, name, value, *name2 in getCheckable(me, params[0]):
                    if 'stat' != t:
                        Database.setMark(me['memberId'], year, name)
                        msg += f"{name} marked"
                await message.channel.send(msg)
