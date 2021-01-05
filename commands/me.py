from commands.base_command  import BaseCommand
from utils import *
from config import Config

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        params = None
        self.aliases = ['m']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        print(message.author.id)
        task = "base"
        if (len(params)>0):
            task=params[0]
        if message.author.id in Config.characters:
            await embedPc(message.channel, Config.characters[message.author.id], task, params)
        else:
            print(Config.characters.keys())



