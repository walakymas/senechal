from commands.base_command import BaseCommand
from config import Config


class Set(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = 0
        params = ['key', 'value']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        Config.config[params[0]] = params[1]
        await message.author.send(f"Set '{params[0]}' to '{params[1]}'")
