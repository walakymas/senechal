from commands.base_command import BaseCommand
from config import Config
from database.markstable import MarksTable
from utils import *


class Winter(BaseCommand):

    def __init__(self):
        description = 'Aktuális játékosra a winter phase fontosabb infóit megadja'
        super().__init__(description, None, ['tel','w'],
                         longdescription='''
Egy extra blokkot igényel a karaktereknél amiben a lovak listája található és ha van aki jobb stewardship ellenőrzést tud adni, akkor azt is.
Ha nincs megadva a blokk, akkor saját stewarshipet használ és 1 charger, 2 rouncy és 2 stumper amit ellenőriz.
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

    async def winter(self, me, message):
        winter = winterData(me)
        year = MarksTable().year()
        embed = get_embed(me)
        major = dice(6)
        msg = f"Gazdaság: {('Terrible','Bad','Normal','Normal','Good','Excellent')[major-1]} ({major})\n"
        (c, t, dobas, siker) = check(int(winter['stewardship']), 0, False)
        if major in (1,2):
            msg += f"Stewardship({winter['stewardship']}): {dobas} {t}  {('Kemény munkával kivédtétek a bajt','Szegény lovag vagy')[siker>=3]} \n"
        elif major == 5:
            msg += f"Extra bevétel: {dice(20)} \n"
        elif major == 6:
            msg += f"Stewardship({winter['stewardship']}): {dobas} {t}  {('Gazdag lovag vagy','Nem sikerült kihasználni a remek időt')[siker>=3]} \n"
        embed.add_field(name=f"{year} tele", value=f"```{msg}```", inline=False)
        msg = ""
        for h in winter['horses']:
            msg += f"  {h}: {('Egészséges','Megdöglött vagy tönkrement')[dice(20)<3]}\n"
        embed.add_field(name="Lovak",value=f"```{msg}```", inline=False)
        i = int(me['memberId'])
        msg = ""
        rows = MarksTable().list(lord=i, year=year)
        msg += f"Modified   Spec              Dobás   Hatás\n";
        marks = []
        for row in rows:
            for t, name, value, *name2 in get_checkable(me, row[5]):
                if name not in marks:
                    marks.append(name)
                    (color, text, ro, success) = check(value, 0)
                    msg += f"{str(row[2])[:10]} {name:15} {ro:2} vs {value:2}  {('---', 'Increase')[ro > value]}\n"
        embed.add_field(name="Pipák",value=f"```{msg}```", inline=False)

        await message.channel.send(embed=embed)
