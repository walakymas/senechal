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
        char = get_me(message)
        year = int(MarksTable.year())
        if char:
            if len(params) == 0 or 'list' == params[0].lower():
                embed = get_embed(char)
                rows = MarksTable().list(dbid=char.id, year=year)
                msg = f"```ID  Modified   Spec\n";
                marks = []
                for row in rows:
                    if row[5] not in marks:
                        marks.append(row[5])
                        msg += f"{row[0]:3} {str(row[2])[:10]} {row[5]:15}\n"
                embed.add_field(name=f"Év: {year} pipák", value=msg+"```", inline=False )
                await message.channel.send(embed=embed)
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
            else:
                msg = f"Year:{year}\n"
                for t, name, value, *name2 in get_checkable(char.get_data(), params[0]):
                    if 'stat' != t:
                        MarksTable().set(char.id, year, name)
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
                        lord = Character.get_by_memberid(last_lord)
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
