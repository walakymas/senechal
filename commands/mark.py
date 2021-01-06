from commands.base_command import BaseCommand
from database.markstable import MarksTable
from utils import *


class Mark(BaseCommand):

    def __init__(self):
        description = '"Pipa" kezelés'
        params = ['spec']
        super().__init__(description, params,longdescription='''Pipa kezelés
        
**!mark list** A bejelölt tulajdonságok listája
**!mark remove {id} Egy jelölés eltávolítása
**!mark spec** Egy-vagy több elem megjelölése 
''')

    async def handle(self, params, message, client):
        me = getMe(message)
        year = int(MarksTable.year())
        if me:
            if 'list' == params[0].lower():
                rows = MarksTable().list()
                msg = f"```{me['name']} Év: {year} \n\nID  Modified   Spec\n";
                marks = []
                for row in rows:
                    if message.author.id == int(row[2]) and year == int(row[1]):
                        if row[3] not in marks:
                            marks.append(row[3])
                            msg += f"{row[4]:3} {row[0][:10]} {row[3]:15}\n"
                await message.channel.send(msg + "```")
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
            else:
                msg = f"Year:{year}\n"
                for t, name, value, *name2 in getCheckable(me, params[0]):
                    if 'stat' != t:
                        MarksTable().set(me['memberId'], year, name)
                        msg += f"{name} marked"
                await message.channel.send(msg)
        else:
            if 'list' == params[0].lower():
                rows = MarksTable().list()
                msg = "```"
                marks = []
                last_lord = 0;
                for row in rows:
                    if int(row[2]) != last_lord:
                        last_lord = int(row[2])
                        lord = Config.characters[last_lord]
                        msg += f"{lord} Év:{year} \nID  Modified            Spec\n";
                    if year == int(row[1]):
                        if row[3] not in marks:
                            marks.append(row[3])
                            msg += f"{row[4]:3} {row[0][:10]} {row[3]:15}\n"
                await message.channel.send(msg + "```")
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
