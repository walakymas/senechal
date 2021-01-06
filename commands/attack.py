from commands.base_command import BaseCommand
from utils import *


class Attack(BaseCommand):

    def __init__(self):
        params = ['spec']
        super().__init__("Támadás próba az aktuális karakternek", params, ['a'],
                         longdescription= '''Támadás próba az aktuális karakternek 
Opcionális paraméterek: módosító, sebzés kockák száma, ellenfél tulajdonsága, ellenfél sebzése''')

    async def handle(self, params, message, client):
        if message.author.id in Config.characters:
            pc = Config.characters[message.author.id]
            if 'memberId' in pc:
                (spec, modifier, damage, base2, damage2) = extract(params, ['---', 0, 0, -1, -1])
                for t, name, value, *name2 in getCheckable(pc, spec):
                    await embedAttack(message.channel, pc, name, value, int(modifier), int(damage), int(base2),
                                      int(damage2))
