from commands.base_command import BaseCommand
from config import Config
from utils import *


class Npc(BaseCommand):

    def __init__(self):
        description = "Npc adatai"
        params = None
        super().__init__(description, ['név'],
                         longdescription='''**!npc {nev} [*|_base_|stats|events|traits|skills] ** információs blokkok a characters.yaml illetve az addatbázisban tárolt eventek alapján
Paraméter nélkül a base blokk jelenik meg, * esetén az összes.
                         ''')

    async def handle(self, params, message, client):
        task = "base"
        if len(params) > 1:
            task = params[1]
        name = "*"
        if len(params) > 0:
            name = params[0]
        count = 0
        for pc in Config.npcs():
            if "*" == name or name.lower() in pc['name'].lower():
                count += 1
                await embed_pc(message.channel, pc, task, params)
        if count == 0:
            await message.channel.send(name + '? Sajnos nem ismerek ilyen lovagot')
