from commands.base_command  import BaseCommand
from utils import *
from config import Config

class Npc(BaseCommand):

    def __init__(self):
        description = "Npc adatai"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        task = "base"
        if len(params)>1:
            task=params[1]
        name ="*"
        if len(params)>0:
            name=params[0]
        count = 0
        for pc in Config.npcs():
            if "*" == name or name.lower() in pc['name'].lower():
                count+=1
                await embedPc(message.channel, pc, task, params)
        if count == 0:
            await message.channel.send(name +'? Sajnos nem ismerek ilyen lovagot')


