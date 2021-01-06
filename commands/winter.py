from commands.base_command import BaseCommand
from config import Config
from database.markstable import MarksTable
from utils import *


class Winter(BaseCommand):

    def __init__(self):
        description = 'Aktuális játékosra a winter phase fontosabb infóit megadja'
        super().__init__(description, None, longdescription=''' Aktuális játékosra a winter phase fontosabb infóit megadja
Egy extra blokkot igényel a karaktereknél amiben a lovak listája található és ha van aki jobb stewardship ellenőrzést tud adni, akkor azt is.
Ha nincs megadva a blokk, akkor saját stewarshipet használ és 1 charger, 2 rouncy és 2 stumper amit ellenőriz.
Ha meg voltak adva ebben az évben ***!mark {skill|trait|passion}*** utasítással pipát kapott tulajdonságok, azokat listázza dob d20-l és közli az eredményt
''')

    async def handle(self, params, message, client):
        me = getMe(message)
        if me:
            year = MarksTable().year()
            msg = f"```{year} tele, {me['name']}\n"
            ss = 0;
            for s in getCheckable(me, 'stewardship'):
                ss = s[3]
            winter = {'stewardship': ss, 'horses':['charger', 'rouncy', 'rouncy', 'stumper', 'stumper' ]}
            if 'winter' in me:
                if 'stewardship' in me['winter']:
                    winter['stewardship'] = me['winter']['stewardship']
                if 'horses' in me['winter']:
                    winter['horses'] = me['winter']['horses']
            major = dice(6)
            msg += f"Gazdaság: {('Terrible','Bad','Normal','Normal','Good','Excellent')[major-1]} ({major})\n"
            (c, t, dobas, siker) = check(winter['stewardship'], 0)
            if major in (1,2):
                msg += f"Stewardship({winter['stewardship']}): {dobas} {successes[siker]}  {('Kemény munkával kivédtétek a bajt','Szegény lovag vagy')[siker>=3]} \n"
            elif major == 5:
                msg += f"Extra bevétel: {dice(20)} \n"
            elif major == 6:
                msg += f"Stewardship({winter['stewardship']}): {dobas} {successes[siker]}  {('Gazdag lovag vagy','Nem sikerült kihasználni a remek időt')[siker>=3]} \n"

            msg += "\nLovak\n"
            for h in winter['horses']:
                msg += f"  {h}: {('Egészséges','Megdöglött vagy tönkrement')[dice(20)<3]}\n"
            rows = MarksTable().list()
            msg += f"\nModified   Spec              Dobás   Hatás\n";
            marks = []
            for row in rows:
                if message.author.id == int(row[2]) and year == int(row[1]):
                    for t, name, value, *name2 in getCheckable(me, row[3]):
                        if name not in marks:
                            marks.append(name)
                            (color, text, ro, success) = check(value, 0)
                            msg += f"{row[0][:10]} {row[3]:15} {ro:2} vs {value:2}  {('---', 'Increase')[ro > value]}\n"

            await message.channel.send(msg + "```")
