from commands.base_command import BaseCommand
from utils import *
from config import Config


class Attack(BaseCommand):

    def __init__(self):
        description = '''Attack check" 
            Opcionális paraméterek: módosító, sebzés kockák száma, ellenfél tulajdonsága, ellenfél sebzése
            '''
        params = ['spec']
        super().__init__(description,params, ['a'])

    async def handle(self, params, message, client):
        if message.author.id in Config.characters:
            pc = Config.characters[message.author.id]
            if 'memberId' in pc:
                (spec, modifier, damage, obase, odamage) = extract(params, ['---',0, 0, -1, -1])
                for t, name, value, *name2 in getCheckable(pc, spec):
                    await embedAttack(message.channel, pc, name, value, int(modifier), int(damage), int(obase),
                                      int(odamage))
