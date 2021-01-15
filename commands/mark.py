from commands.base_command import BaseCommand
from database.markstable import MarksTable
from utils import *


class Mark(BaseCommand):

    def __init__(self):
        description = '"Pipa" kezelés'
        params = ['spec']
        super().__init__(description, None, aliases=['pipa'],
                         longdescription='''**!mark list** A bejelölt tulajdonságok listája
**!mark remove {id}** Egy jelölés eltávolítása
**!mark {spec}** Egy-vagy több elem megjelölése 
''')

    async def handle(self, params, message, client):
        me = get_me(message)
        year = int(MarksTable.year())
        if me:
            if len(params) == 0 or 'list' == params[0].lower():
                rows = MarksTable().list(lord=me['memberId'], year=year)
                msg = f"```{me['name']} Év: {year} \n\nID  Modified   Spec\n";
                marks = []
                for row in rows:
                    if row[3] not in marks:
                        marks.append(row[3])
                        msg += f"{row[4]:3} {row[0][:10]} {row[3]:15}\n"
                await message.channel.send(msg + "```")
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
            else:
                msg = f"Year:{year}\n"
                for t, name, value, *name2 in get_checkable(me, params[0]):
                    if 'stat' != t:
                        MarksTable().set(me['memberId'], year, name)
                        msg += f"{name} marked"
                await message.channel.send(msg)
        else:
            if len(params) == 0 or 'list' == params[0].lower():
                rows = MarksTable().list()
                msg = ""
                marks = []
                last_lord = 0;
                for row in rows:
                    if int(row[2]) != last_lord:
                        last_lord = int(row[2])
                        lord = Config.characters[last_lord]
                        msg += f"\n{lord['name']} Év:{year} \n ID Modified   Spec\n";
                        marks = []
                    if year == int(row[1]):
                        if row[3] not in marks:
                            marks.append(row[3])
                            msg += f"{row[4]:3} {row[0][:10]} {row[3]:15}\n"
                await message.channel.send("```" + msg.strip() + "```")
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
