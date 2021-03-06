from commands.base_command import BaseCommand
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
        for char in Character.npcs(name):
            count += 1
            await embed_char(message.channel, char, task, params, client, message)
        if count == 0:
            await message.channel.send(name + '? Sajnos nem ismerek ilyen lovagot')
