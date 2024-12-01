from commands.base_command import BaseCommand
from config import Config
from utils import *


class Winter(BaseCommand):

    def __init__(self):
        description = 'Aktuális játékosra a winter phase fontosabb infóit megadja'
        super().__init__(description, None, ['tel'],
                         longdescription='''
Egy extra blokkot igényel a karaktereknél amiben a lovak listája található és ha van aki jobb stewardship ellenőrzést tud adni, akkor azt is.
Ha nincs megadva a blokk, akkor saját stewardshipet használ és 1 charger, 2 rouncy és 2 stumper amit ellenőriz.
Ha meg voltak adva ebben az évben ***!mark {skill|trait|passion}*** utasítással pipát kapott tulajdonságok, azokat listázza dob d20-l és közli az eredményt
''')

    async def handle(self, params, message, client):
        me = get_me(message)
        if me:
            await self.winter(me, message)
        elif len(params) > 0:
            print(params[0])
            for pc in Config.pcs():
                await self.winter(pc, message)

    async def winter(self, char, message):
        winter = winterData(char)
        year = MarksTable().year()
        embed = get_embed(char)
        major = dice(6)
        msg = f"Gazdaság: {('Terrible','Bad','Normal','Normal','Good','Excellent')[major-1]} ({major})\n"
        (c, t, dobas, siker) = check(int(winter['stewardship']), 0, False)
        if major in (1,2):
            msg += f"Stewardship({winter['stewardship']}): {dobas} {t}  {('Kemény munkával kivédtétek a bajt','Szegény lovag vagy')[siker>=3]} \n"
        elif major == 5:
            msg += f"Extra bevétel: {dice(20)} \n"
        elif major == 6:
            msg += f"Stewardship({winter['stewardship']}): {dobas} {t}  {('Gazdag lovag vagy','Nem sikerült kihasználni a remek időt')[siker>=3]} \n"
        #embed.add_field(name=f"{year} tele", value=f"```{msg}```", inline=False)
        msg = ""
        for h in winter['horses']:
            msg += f"  {h}: {('Egészséges','Megdöglött vagy tönkrement')[dice(20)<3]}\n"
        #embed.add_field(name="Lovak",value=f"```{msg}```", inline=False)
        charId = int(char.id)
        msg = ""
        rows = MarksTable().list(dbid=charId, year=year)
        msg += f"Modified   Spec              Dobás   Hatás\n";
        marks = []
        for row in rows:
            for t, name, value, *name2 in get_checkable(char.get_data(), row[5]):
                if name not in marks:
                    marks.append(name)
                    (color, text, ro, success) = check(value, 0)
                    msg += f"{str(row[2])[:10]} {name:15} {ro:2} vs {value:2}  {('---', 'Increase')[ro > value]}\n"
        embed.add_field(name="Pipák", value=f"```{msg}```", inline=False)
        xp = 0
        for n, v in char.data['traits'].items():
            if v >= 16:
                xp += v
            elif v <= 4:
                xp += 20 - v
        for n, v in char.data['passions'].items():
            if v >= 16:
                xp += v
        if xp > 0:
            embed.add_field(name="Extra Glory", value=f"`{xp}`", inline=False)
        if 'npcs' in char.data:
            for nf,  f in char.data['npcs'].items():
                s = ""
                if 'dbid' in f:
                    npc = Character.get_by_id(f['dbid'])
                    if 'Deceased' in npc.data['main']:
                        s = f"NPC is dead ({npc.data['main']['Deceased']})\n"
                    else:
                        rows = MarksTable().list(dbid=f['dbid'], year=year)
                        marks = []
                        if 'role' in f and (f['role'] == 'wife' or f['role'] == 'lover'):
                            birth = 0
                            con = npc.data['stats']['con']
                            if 'birth' in npc.data['main']:
                                birth = npc.data['main']['birth']
                            s += f"Con: {con}, Birth: {birth} \n"

                        s += f"Modified   Spec              Dobás   Hatás\n";
                        for row in rows:
                            #print(f"{row}")
                            for t, name, value, *name2 in get_checkable(npc.get_data(), row[5]):
                                if name not in marks:
                                    marks.append(name)
                                    (color, text, ro, success) = check(value, 0)
                                    s += f"{str(row[2])[:10]} {name:15} {ro:2} vs {value:2}  {('---', 'Increase')[ro > value]}\n"
                    if s != "":
                        embed.add_field(name=f"{npc.data['name']} ({f['connection']})", value=f"```{s}```", inline=False)
                else:
                    if 'skills' in f:
                        for n, v in f['skills'].items():
                            if v < 15 or (v <= 20 and randint(1, 6) == 6) or (v > 20 and randint(1, 20) == 20):
                                s += f"{n} `{v}` -> `{v+1}`\n"
                    if s != "":
                        embed.add_field(name=f"{nf} ({f['connection']})", value=s, inline=False)
        await message.channel.send(embed=embed)
