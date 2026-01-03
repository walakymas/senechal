from commands.base_command import BaseCommand
from config import Config


class Set(BaseCommand):

    def __init__(self):
        description = 'Egyes beállítások ideiglenes felülbírálása főként teszt célokra'
        params = ['key', 'value']
        super().__init__(description, params, longdescription='''Jelenleg két key van kezelve:
**debugdice:** minden dobás értéke a paraméterben megadott érték legyen
**debugme:** fix user id, az üzenet küldőjétől függetlenül. így megnézhetem másnak mi jelenne meg.''')

    async def handle(self, params, message, client):
        if params[1] == '---':
            Config.config.pop(params[0], None)  # Remove the entry if value is '---'
            await message.author.send(f"Unset '{params[0]}'")
        else:
            Config.config[params[0]] = params[1]
            await message.author.send(f"Set '{params[0]}' to '{params[1]}'")
