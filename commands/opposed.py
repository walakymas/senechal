from commands.base_command import BaseCommand
from config import Config
from utils import *


class Opposed(BaseCommand):

    def __init__(self):
        description = "Opposed check"
        params = ["spec"]
        super().__init__(description, params, ['o'])

    async def handle(self, params, message, client):
        if message.author.id in Config.characters:
            pc = Config.characters[message.author.id]
            (spec, *extra) = params
            (modifier, obase) = extract(extra, [0, -1])
            if 'memberId' in pc:
                for t, name, value, *name2 in getCheckable(pc, spec):
                    await embedAttack(message.channel, pc, name, value, int(modifier), -1, int(obase), -1)
