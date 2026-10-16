import logging
from commands.base_command import BaseCommand
from config import Config
from permissions import has_rights, NO_RIGHTS
from utils import *
from winter_logic import run_winter

log = logging.getLogger(__name__)


class Winter(BaseCommand):

    def __init__(self):
        description = 'Aktuális játékosra a winter phase fontosabb infóit megadja'
        super().__init__(description, None, ['tel'],
                         longdescription='''
Egy extra blokkot igényel a karaktereknél amiben a lovak listája található és ha van aki jobb stewardship ellenőrzést tud adni, akkor azt is.
Ha nincs megadva a blokk, akkor saját stewardshipet használ és 1 charger, 2 rouncy és 2 stumper amit ellenőriz.
Ha meg voltak adva ebben az évben ***!mark {skill|trait|passion}*** utasítással pipát kapott tulajdonságok, akkor az Unchecked állapotúakra dob d20-at: az érték vagy kevesebb = Failed, nagyobb (20 feletti értéknél 20) = Increase. Az eredmény a pipa állapotában marad, az már elvégzett próbákat nem dobja újra (az Increase-ek növelése: ***!mark update***).
A teljes eredmény új eseményként bekerül a karakter eseményei közé.
**!winter force** (csak admin) minden próbát újradob, az Updated pipák kivételével.
''')

    async def handle(self, params, message, client):
        words = message.content[len(Config.prefix):].split()
        force = any(w.lower() == 'force' for w in words[1:])
        if force and not has_rights(message.author.id):
            await message.channel.send(message.author.mention + NO_RIGHTS)
            return
        me = get_me(message, words=[w for w in words if w.lower() != 'force'])
        if me:
            await self.winter(me, message, force)
        elif len(params) > 0:
            for pc in Character.pcs():
                await self.winter(pc, message, force)

    async def winter(self, char, message, force=False):
        result = run_winter(char, force)
        await send_embed_fields(message.channel, char, result.embed_fields())
