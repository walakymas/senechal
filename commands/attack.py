from commands.base_command import BaseCommand
from utils import *


class Attack(BaseCommand):

    def __init__(self):
        params = ['spec']
        super().__init__("Támadás próba az aktuális karakternek", params, ['a'],
                         longdescription= '''Támadás próba az aktuális karakternek
                         
**!attack {skill} *{modoító}* *{sebzés kockák}* *{ellenfél skill}* *{ellenfél sebzés kockák}* **
Kritikus siker esetén mindkét oldal esetén automatikusan 4 kockával növeli a sebzést. 
''')

    async def handle(self, params, message, client):
        pc = get_me(message)
        if pc:
            (spec, modifier, damage, base2, damage2) = extract(params, ['---', 0, 0, -1, -1])
            for t, name, value, *name2 in get_checkable(pc, spec):
                await embed_attack(message.channel, pc, name, value, int(modifier), int(damage), int(base2), int(damage2))
