from commands.base_command import BaseCommand
from database.markstable import MarksTable
from utils import *
from winter_logic import update_marks


class Mark(BaseCommand):

    def __init__(self):
        description = '"Pipa" kezelés'
        params = ['spec']
        super().__init__(description, None, aliases=['pipa'],
                         longdescription='''**!mark list** A bejelölt tulajdonságok listája
**!mark remove {id}** Egy jelölés eltávolítása
**!mark update** Az aktuális év Increase állapotú (winter során sikeres) jelöléseinek növelése eggyel, a jelölés Updated lesz
**!mark {spec}** Egy-vagy több elem megjelölése 
''')

    async def handle(self, params, message, client):
        char = get_me(message)
        year = int(MarksTable.year())
        if char:
            if len(params) == 0 or 'list' == params[0].lower():
                embed = get_embed(char)
                rows = MarksTable().list(dbid=char.id, year=year)
                msg = f"```ID  Modified   Spec            Status\n";
                marks = []
                for row in rows:
                    if row[5] not in marks:
                        marks.append(row[5])
                        msg += f"{row[0]:3} {str(row[2])[:10]} {row[5]:15} {row[7]}\n"
                embed.add_field(name=f"Év: {year} pipák", value=msg+"```", inline=False )
                await message.channel.send(embed=embed)
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
            elif 'update' == params[0].lower():
                changes = update_marks(char.id, year)
                if changes:
                    msg = f"Year:{year}\n" + "".join(f"{n}: {o} -> {v}\n" for n, o, v in changes)
                else:
                    msg = f"Year:{year}\nNincs növelendő (Increase állapotú) pipa"
                await message.channel.send(msg)
            else:
                msg = f"Year:{year}\n"
                for t, name, value, *name2 in get_checkable(char.get_data(), params[0]):
                    if 'stat' != t:
                        MarksTable().set(char.id, year, name)
                        msg += f"{name} marked"
                await message.channel.send(msg)
        else:
            if len(params) == 0 or 'list' == params[0].lower():
                # marks table columns: id, created, modified, year, lord, spec, dbid
                rows = MarksTable().list(year=year)
                msg = ""
                marks = []
                last_dbid = None
                for row in rows:
                    if row[6] != last_dbid:
                        last_dbid = row[6]
                        lord = Character.get_by_id(last_dbid)
                        msg += f"\n{lord.name if lord else last_dbid} Év:{year} \n ID Modified   Spec            Status\n";
                        marks = []
                    if row[5] not in marks:
                        marks.append(row[5])
                        msg += f"{row[0]:3} {str(row[2])[:10]} {row[5]:15} {row[7]}\n"
                await message.channel.send("```" + msg.strip() + "```")
            elif 'remove' == params[0].lower():
                MarksTable().remove(params[1])
                await message.channel.send("removed")
